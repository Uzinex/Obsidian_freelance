from django.db import migrations

RED_FLAGS = [
    (
        "fraud_offplatform",
        "Запрос перевода вне платформы",
        "fraud",
        r"(western union|moneygram|перевед[её]те на карту)",
        "high",
    ),
    (
        "banned_payment_details",
        "Указание запрещённых реквизитов",
        "banned_payment",
        r"(iban|swift|crypto|btc|usdt)",
        "medium",
    ),
    (
        "insult",
        "Оскорбление пользователя",
        "abuse",
        r"(идиот|тупиц|ненавижу тебя)",
        "medium",
    ),
    (
        "spam_offer",
        "Реклама вне платформы",
        "spam",
        r"(подписывайтесь на мой телеграм|жми ссылку)",
        "low",
    ),
]


def seed_patterns(apps, schema_editor):
    Pattern = apps.get_model("moderation", "ChatRedFlagPattern")
    for code, label, category, pattern, severity in RED_FLAGS:
        Pattern.objects.get_or_create(
            code=code,
            defaults={
                "label": label,
                "category": category,
                "pattern": pattern,
                "severity": severity,
            },
        )


def unseed(apps, schema_editor):
    Pattern = apps.get_model("moderation", "ChatRedFlagPattern")
    Pattern.objects.filter(code__in=[code for code, *_ in RED_FLAGS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("moderation", "0001_initial"),
    ]

    operations = [migrations.RunPython(seed_patterns, unseed)]
