from django.db import migrations
from django.utils.text import slugify


CATEGORY_DATA = {
    "Marketing": [
        "Производственный маркетинг",
        "Товарный маркетинг",
        "Сбытовой маркетинг",
        "Рыночный маркетинг",
        "Социальный маркетинг",
        "Интернет маркетинг",
        "Международный маркетинг",
    ],
    "Услуги администрации": [
        "Администрация чата",
        "Админ предприятия",
        "Оператор колл-центра",
    ],
    "Дизайн": [
        "Веб дизайн",
        "Графический дизайн",
        "Дизайн товара",
        "Интерьер/экстерьер дизайн",
        "Мультимедийный дизайн",
        "Иллюстрация",
        "Ландшафтный дизайн",
    ],
    "Услуги редактирования": [
        "Редактирование текста",
        "Редактирование изображения",
        "Редактирование контента",
        "Редактирование книг",
    ],
    "Программирование": [
        "Вэб программирование",
        "Мобильное программирование",
        "Программирование игр",
        "Системное программирование",
        "Разработка базы данных",
        "Кибер безопасность",
        "Вэб разработка",
        "Верстка",
        "GitHub",
        "JavaScript",
        "Java",
        "C++",
        "C#",
        "Python",
        "Django",
        "React",
        "Node.js",
        "Flask",
        "Arduino",
        "HTML",
        "CSS",
        "PHP",
        "TypeScript",
        "Go",
        "Kotlin",
        "Swift",
        "Rust",
        "SQL",
    ],
    "Услуги видео и аудио": [
        "Видео съемка",
        "Видеомонтаж",
        "Создание анимации и графики",
        "Видео реклама",
        "Озвучка и дубляж",
        "Трансляция и стриминг",
        "Запись звука",
        "Редактирование видео и аудио",
    ],
    "Искусственный интеллект": [
        "Создание AI видео",
        "Создание AI фото",
        "Создание AI контента",
    ],
}


def _generate_unique_slug(model, base_slug):
    """Return a slug that is unique for the given model."""

    if not base_slug:
        base_slug = "item"

    unique_slug = base_slug
    counter = 1

    while model.objects.filter(slug=unique_slug).exists():
        counter += 1
        unique_slug = f"{base_slug}-{counter}"

    return unique_slug


def seed_categories_and_skills(apps, schema_editor):
    Category = apps.get_model("marketplace", "Category")
    Skill = apps.get_model("marketplace", "Skill")

    for category_name, skills in CATEGORY_DATA.items():
        category_slug = slugify(category_name, allow_unicode=True)
        category_slug = _generate_unique_slug(Category, category_slug)
        category, created = Category.objects.get_or_create(
            name=category_name,
            defaults={
                "slug": category_slug,
                "description": category_name,
            },
        )
        if not category.slug:
            category.slug = _generate_unique_slug(
                Category, slugify(category_name, allow_unicode=True)
            )
            category.save(update_fields=["slug"])
        for skill_name in skills:
            skill_slug = slugify(skill_name, allow_unicode=True)
            skill_slug = _generate_unique_slug(Skill, skill_slug)
            skill, created = Skill.objects.get_or_create(
                name=skill_name,
                defaults={
                    "slug": skill_slug,
                    "category": category,
                },
            )
            if not created and not skill.slug:
                skill.slug = _generate_unique_slug(Skill, skill_slug)
                skill.save(update_fields=["slug"])


def unseed_categories_and_skills(apps, schema_editor):
    Category = apps.get_model("marketplace", "Category")
    Skill = apps.get_model("marketplace", "Skill")

    skill_names = [skill for skills in CATEGORY_DATA.values() for skill in skills]
    Skill.objects.filter(name__in=skill_names).delete()
    Category.objects.filter(name__in=CATEGORY_DATA.keys()).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("marketplace", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_categories_and_skills, unseed_categories_and_skills),
    ]
