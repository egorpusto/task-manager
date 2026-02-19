from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone


@shared_task
def send_deadline_reminders() -> int:

    from .models import Task

    now = timezone.now()
    in_24h = now + timezone.timedelta(hours=24)

    upcoming_tasks = (
        Task.objects.filter(
            deadline__gte=now,
            deadline__lte=in_24h,
        )
        .exclude(status=Task.Status.DONE)
        .select_related("user")
    )

    tasks_by_user: dict = {}
    for task in upcoming_tasks:
        tasks_by_user.setdefault(task.user, []).append(task)

    sent = 0
    for user, tasks in tasks_by_user.items():
        if not user.email:
            continue

        task_lines = "\n".join(
            f"- {task.title} (deadline: {task.deadline.strftime('%d %b %Y %H:%M')})"
            for task in tasks
        )
        send_mail(
            subject="Task Manager: upcoming deadlines",
            message=(
                f"Hi {user.username},\n\n"
                f"You have {len(tasks)} task(s) due in the next 24 hours:\n\n"
                f"{task_lines}\n\n"
                "Stay on top of it!"
            ),
            from_email=None,
            recipient_list=[user.email],
        )
        sent += 1

    return sent
