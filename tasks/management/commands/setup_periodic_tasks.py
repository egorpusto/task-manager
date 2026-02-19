from django.core.management.base import BaseCommand
from django_celery_beat.models import CrontabSchedule, PeriodicTask


class Command(BaseCommand):
    help = "Creates periodic tasks for Celery Beat"

    def handle(self, *args, **options):
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute="0",
            hour="8",
            day_of_week="*",
            day_of_month="*",
            month_of_year="*",
        )

        task, created = PeriodicTask.objects.get_or_create(
            name="Send deadline reminders",
            defaults={
                "task": "tasks.tasks.send_deadline_reminders",
                "crontab": schedule,
            },
        )

        if created:
            self.stdout.write(self.style.SUCCESS("Periodic task created."))
        else:
            self.stdout.write("Periodic task already exists.")
