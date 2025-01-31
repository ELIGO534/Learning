from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.contrib.admin.models import LogEntry

class Command(BaseCommand):
    help = 'Cleanup old logs from the database'

    def handle(self, *args, **kwargs):
        # Define how old logs should be (e.g., older than 30 days)
        delete_before = timezone.now() - timedelta(days=30)

        # Query to delete logs older than the specified time
        deleted, _ = LogEntry.objects.filter(action_time__lt=delete_before).delete()

        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {deleted} old log(s).'))
