from datetime import timedelta
from decimal import Decimal

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from marketplace.models import Category, Order, Skill

from obsidian_backend import jwt_settings as jwt_conf

from .models import Profile, User


class ProfileSerializerTests(APITestCase):
    def setUp(self):
        self.user = User(
            nickname="tester",
            email="tester@example.com",
            first_name="Test",
            last_name="User",
        )
        self.user.set_password("StrongPass123!")
        self.user.save()
        self.client.force_authenticate(user=self.user)

    def test_profile_update_accepts_null_strings(self):
        create_payload = {
            "role": Profile.ROLE_FREELANCER,
            "freelancer_type": Profile.FREELANCER_TYPE_INDIVIDUAL,
            "company_registered_as": Profile.REGISTRATION_TYPE_NONE,
            "skills": [],
        }
        create_response = self.client.post(
            reverse("profile-list"), create_payload, format="json"
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        profile_id = create_response.data["id"]

        update_response = self.client.patch(
            reverse("profile-detail", args=[profile_id]),
            {
                "company_name": None,
                "company_city": None,
                "phone_number": None,
                "country": None,
            },
            format="json",
        )

        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data["company_name"], "")
        self.assertEqual(update_response.data["company_city"], "")
        self.assertEqual(update_response.data["phone_number"], "")
        self.assertEqual(update_response.data["country"], "")

        profile = Profile.objects.get(id=profile_id)
        self.assertEqual(profile.company_name, "")
        self.assertEqual(profile.company_city, "")
        self.assertEqual(profile.phone_number, "")
        self.assertEqual(profile.country, "")

    def test_profile_update_allows_existing_skills(self):
        category = Category.objects.create(name="Testing", slug="testing")
        skill = Skill.objects.create(name="QA", slug="qa", category=category)
        create_response = self.client.post(
            reverse("profile-list"),
            {
                "role": Profile.ROLE_FREELANCER,
                "freelancer_type": Profile.FREELANCER_TYPE_INDIVIDUAL,
                "company_registered_as": Profile.REGISTRATION_TYPE_NONE,
                "skills": [],
            },
            format="json",
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        profile_id = create_response.data["id"]

        update_response = self.client.patch(
            reverse("profile-detail", args=[profile_id]),
            {"skills": [skill.id]},
            format="json",
        )

        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data["skills"], [skill.id])
        self.assertTrue(
            Profile.objects.get(id=profile_id).skills.filter(id=skill.id).exists()
        )


class OrderRBACPermissionTests(APITestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(
            nickname="client", email="client@example.com", password="Str0ngPass!",
            first_name="Client", last_name="User",
        )
        self.client_profile = Profile.objects.create(
            user=self.client_user,
            role=Profile.ROLE_CLIENT,
            is_verified=True,
        )
        self.order = Order.objects.create(
            title="Test order",
            description="Secure",
            deadline=timezone.now() + timedelta(days=7),
            payment_type=Order.PAYMENT_FIXED,
            budget=Decimal("1000.00"),
            currency=Order.CURRENCY_UZS,
            order_type=Order.ORDER_TYPE_STANDARD,
            client=self.client_profile,
        )
        self.freelancer_user = User.objects.create_user(
            nickname="freelancer", email="freelancer@example.com", password="Str0ngPass!",
            first_name="Free", last_name="Lancer",
        )
        Profile.objects.create(
            user=self.freelancer_user,
            role=Profile.ROLE_FREELANCER,
            is_verified=True,
        )
        self.staff_user = User.objects.create_user(
            nickname="staffer", email="staff@example.com", password="Str0ngPass!",
            first_name="Staff", last_name="User",
            is_staff=True,
        )

    def test_client_can_update_own_order(self):
        self.client.force_authenticate(user=self.client_user)
        response = self.client.patch(
            reverse("order-detail", args=[self.order.id]),
            {"title": "Updated"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.title, "Updated")

    def test_unverified_client_cannot_update_order(self):
        self.client_profile.is_verified = False
        self.client_profile.save(update_fields=["is_verified"])
        self.client.force_authenticate(user=self.client_user)
        response = self.client.patch(
            reverse("order-detail", args=[self.order.id]),
            {"title": "Blocked"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_freelancer_cannot_update_foreign_order(self):
        self.client.force_authenticate(user=self.freelancer_user)
        response = self.client.patch(
            reverse("order-detail", args=[self.order.id]),
            {"title": "Malicious"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_update_any_order(self):
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.patch(
            reverse("order-detail", args=[self.order.id]),
            {"title": "Staff Update"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class LoginViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            nickname="loginuser",
            email="login@example.com",
            password="StrongPass123!",
            first_name="Login",
            last_name="Tester",
        )

    def test_login_generates_device_id_when_missing(self):
        response = self.client.post(
            reverse("login"),
            {"credential": "loginuser", "password": "StrongPass123!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("session", response.data)
        device_id = response.data["session"].get("device_id")
        self.assertTrue(device_id)
        self.assertLessEqual(len(device_id), 128)
        cookie = response.cookies.get(jwt_conf.JWT_REFRESH_COOKIE.name)
        self.assertIsNotNone(cookie)
