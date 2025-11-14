from django.db import migrations


ADMIN_EMAIL = "fdilov1@gmail.com"


def _assign_admin_role(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    try:
        user = User.objects.get(email__iexact=ADMIN_EMAIL)
    except User.DoesNotExist:
        return
    user.is_staff = True
    user.is_superuser = True
    user.save(update_fields=["is_staff", "is_superuser"])


def _noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0008_auditevent_span_id_auditevent_status_code_and_more"),
    ]

    operations = [
        migrations.RunPython(_assign_admin_role, reverse_code=_noop),
    ]
