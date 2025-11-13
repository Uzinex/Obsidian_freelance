from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from marketplace.models import Category, Skill

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
