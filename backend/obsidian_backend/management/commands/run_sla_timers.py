from django.core.management.base import BaseCommand

from obsidian_backend.sla import process_sla_timers


class Command(BaseCommand):
    help = "Process SLA timers, reminders and auto-actions"

    def handle(self, *args, **options):
        result = process_sla_timers()
        self.stdout.write(
            self.style.SUCCESS(
                "SLA timers processed: "
                f"{result.reminders} reminders, {result.escalations} escalations, {result.auto_releases} auto releases"
            )
        )
