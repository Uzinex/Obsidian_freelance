from __future__ import annotations

from dataclasses import dataclass

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import Profile, Wallet
from marketplace.models import Category, Skill

DEFAULT_PASSWORD = "ChangeMe!123"


@dataclass
class SeedSkill:
    slug: str
    name: str


@dataclass
class SeedCategory:
    slug: str
    name: str
    description: str
    skills: tuple[SeedSkill, ...]


SEED_CATEGORIES: tuple[SeedCategory, ...] = (
    SeedCategory(
        slug="design-creative",
        name="Design & Creative",
        description="Creative disciplines for producing visual assets and brand identities.",
        skills=(
            SeedSkill(slug="brand-identity", name="Brand Identity Design"),
            SeedSkill(slug="ux-research", name="UX Research"),
            SeedSkill(slug="illustration", name="Digital Illustration"),
        ),
    ),
    SeedCategory(
        slug="development-tech",
        name="Development & Tech",
        description="Software engineering, automation, and data skills for product delivery.",
        skills=(
            SeedSkill(slug="django-dev", name="Django Development"),
            SeedSkill(slug="frontend-spa", name="Frontend SPA Development"),
            SeedSkill(slug="data-analytics", name="Data Analytics"),
        ),
    ),
    SeedCategory(
        slug="marketing-growth",
        name="Marketing & Growth",
        description="Demand generation, content, and campaign execution services.",
        skills=(
            SeedSkill(slug="content-strategy", name="Content Strategy"),
            SeedSkill(slug="seo-specialist", name="SEO Specialist"),
            SeedSkill(slug="paid-ads", name="Paid Advertising"),
        ),
    ),
)


SEED_USERS = (
    {
        "nickname": "demo_client",
        "email": "demo.client@example.com",
        "first_name": "Demo",
        "last_name": "Client",
        "role": Profile.ROLE_CLIENT,
        "profile": {
            "company_name": "Acme Demo Holdings",
            "company_country": "Freedonia",
            "company_city": "Northbridge",
            "company_street": "Central Square 42",
            "phone_number": "+1-555-0101",
            "is_verified": False,
            "skills": (),
        },
    },
    {
        "nickname": "demo_freelancer",
        "email": "demo.freelancer@example.com",
        "first_name": "Demo",
        "last_name": "Freelancer",
        "role": Profile.ROLE_FREELANCER,
        "profile": {
            "freelancer_type": Profile.FREELANCER_TYPE_INDIVIDUAL,
            "country": "Freedonia",
            "city": "Lakeside",
            "street": "Innovation Ave",
            "house": "7B",
            "phone_number": "+1-555-0123",
            "is_verified": False,
            "skills": (
                "django-dev",
                "frontend-spa",
                "ux-research",
            ),
        },
    },
)


class Command(BaseCommand):
    help = "Populate deterministic demo categories, skills, and users with safe fake data."

    def handle(self, *args, **options):
        with transaction.atomic():
            categories = self._create_categories_with_skills()
            skills_by_slug = {
                skill.slug: skill
                for category_skills in categories.values()
                for skill in category_skills
            }
            users = self._create_users(skills_by_slug)

        self.stdout.write(self.style.SUCCESS("Demo data successfully prepared."))
        self.stdout.write(self.style.HTTP_INFO(f"Categories touched: {len(categories)}"))
        self.stdout.write(self.style.HTTP_INFO(f"Users touched: {len(users)}"))

    def _create_categories_with_skills(self) -> dict[str, list[Skill]]:
        created_skills: dict[str, list[Skill]] = {}
        for category_seed in SEED_CATEGORIES:
            category, created = Category.objects.get_or_create(
                slug=category_seed.slug,
                defaults={
                    "name": category_seed.name,
                    "description": category_seed.description,
                },
            )
            if not created:
                Category.objects.filter(pk=category.pk).update(
                    name=category_seed.name,
                    description=category_seed.description,
                )
                category.refresh_from_db(fields=["name", "description"])

            created_skills[category_seed.slug] = []
            for skill_seed in category_seed.skills:
                skill, skill_created = Skill.objects.get_or_create(
                    slug=skill_seed.slug,
                    defaults={
                        "name": skill_seed.name,
                        "category": category,
                    },
                )
                if not skill_created:
                    Skill.objects.filter(pk=skill.pk).update(
                        name=skill_seed.name,
                        category=category,
                    )
                    skill.refresh_from_db(fields=["name", "category"])

                created_skills[category_seed.slug].append(skill)
        return created_skills

    def _create_users(self, skills_by_slug: dict[str, Skill]) -> list[str]:
        user_model = get_user_model()
        processed_users: list[str] = []

        for user_seed in SEED_USERS:
            user_defaults = {
                "email": user_seed["email"],
                "first_name": user_seed["first_name"],
                "last_name": user_seed["last_name"],
            }
            user, created = user_model.objects.get_or_create(
                nickname=user_seed["nickname"],
                defaults=user_defaults,
            )
            for field, value in user_defaults.items():
                setattr(user, field, value)
            user.set_password(DEFAULT_PASSWORD)
            user.save()

            profile_defaults = {
                "role": user_seed["role"],
                "freelancer_type": user_seed["profile"].get("freelancer_type", ""),
                "company_name": user_seed["profile"].get("company_name", ""),
                "company_country": user_seed["profile"].get("company_country", ""),
                "company_city": user_seed["profile"].get("company_city", ""),
                "company_street": user_seed["profile"].get("company_street", ""),
                "phone_number": user_seed["profile"].get("phone_number", ""),
                "country": user_seed["profile"].get("country", ""),
                "city": user_seed["profile"].get("city", ""),
                "street": user_seed["profile"].get("street", ""),
                "house": user_seed["profile"].get("house", ""),
                "is_completed": True,
                "is_verified": user_seed["profile"].get("is_verified", False),
            }
            profile, profile_created = Profile.objects.get_or_create(
                user=user,
                defaults=profile_defaults,
            )
            if not profile_created:
                for field, value in profile_defaults.items():
                    setattr(profile, field, value)
                profile.save()

            # Assign skills if provided
            skill_slugs = user_seed["profile"].get("skills", ())
            if skill_slugs:
                resolved_skills = [
                    skills_by_slug[slug]
                    for slug in skill_slugs
                    if slug in skills_by_slug
                ]
                profile.skills.set(resolved_skills)
            else:
                profile.skills.clear()

            Wallet.objects.get_or_create(profile=profile)

            processed_users.append(user.nickname)
        return processed_users
