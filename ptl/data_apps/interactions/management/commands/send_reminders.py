from django.core.management.base import BaseCommand, CommandError

from ...models import send_reminders


class Command(BaseCommand):
    help = "Send reminders to all users who should receive them."

    def handle(self, *args, **options):
        send_reminders()
