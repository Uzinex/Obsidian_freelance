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


def seed_categories_and_skills(apps, schema_editor):
    Category = apps.get_model("marketplace", "Category")
    Skill = apps.get_model("marketplace", "Skill")

    for category_name, skills in CATEGORY_DATA.items():
        category, _ = Category.objects.get_or_create(
            name=category_name,
            defaults={
                "slug": slugify(category_name, allow_unicode=True),
                "description": category_name,
            },
        )
        if not category.slug:
            category.slug = slugify(category_name, allow_unicode=True)
            category.save(update_fields=["slug"])
        for skill_name in skills:
            Skill.objects.get_or_create(
                name=skill_name,
                defaults={
                    "slug": slugify(skill_name, allow_unicode=True),
                    "category": category,
                },
            )


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
