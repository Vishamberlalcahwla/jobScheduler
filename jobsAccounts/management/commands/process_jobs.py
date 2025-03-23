from django.core.management.base import BaseCommand
from jobsAccounts.utils import schedule_jobs

class Command(BaseCommand):
    help = "Process scheduled jobs (Max 3 at a time)"

    def handle(self, *args, **kwargs):
        schedule_jobs()
        self.stdout.write(self.style.SUCCESS("✅ Successfully processed jobs."))
