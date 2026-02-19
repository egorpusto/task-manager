import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from tasks.models import Tag, Task

User = get_user_model()


# ─── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", password="testpass123")


@pytest.fixture
def other_user(db):
    return User.objects.create_user(username="otheruser", password="testpass123")


@pytest.fixture
def task(user):
    return Task.objects.create(user=user, title="Test Task", status=Task.Status.TODO)


@pytest.fixture
def auth_client(client, user):
    client.login(username="testuser", password="testpass123")
    return client


# ─── Model tests ──────────────────────────────────────────────────────────────


class TestTagModel:
    def test_str(self, db):
        tag = Tag.objects.create(name="urgent")
        assert str(tag) == "urgent"

    def test_unique(self, db):
        Tag.objects.create(name="work")
        with pytest.raises(Exception):
            Tag.objects.create(name="work")


class TestTaskModel:
    def test_str(self, task):
        assert str(task) == "Test Task"

    def test_default_status(self, task):
        assert task.status == Task.Status.TODO

    def test_default_priority(self, task):
        assert task.priority == Task.Priority.MEDIUM

    def test_ordering(self, user, db):
        Task.objects.create(user=user, title="First")
        second = Task.objects.create(user=user, title="Second")
        assert Task.objects.first() == second

    def test_is_overdue_true(self, user, db):
        past = timezone.now() - timezone.timedelta(hours=1)
        task = Task.objects.create(
            user=user, title="Overdue", deadline=past, status=Task.Status.TODO
        )
        assert task.is_overdue is True

    def test_is_overdue_false_when_done(self, user, db):
        past = timezone.now() - timezone.timedelta(hours=1)
        task = Task.objects.create(
            user=user, title="Done", deadline=past, status=Task.Status.DONE
        )
        assert task.is_overdue is False

    def test_is_overdue_false_when_no_deadline(self, task):
        assert task.is_overdue is False


# ─── View tests ───────────────────────────────────────────────────────────────


class TestTaskListView:
    def test_requires_login(self, client):
        response = client.get(reverse("task_list"))
        assert response.status_code == 302
        assert "/accounts/login/" in response["Location"]

    def test_authenticated(self, auth_client, task):
        response = auth_client.get(reverse("task_list"))
        assert response.status_code == 200
        assert "Test Task" in response.content.decode()

    def test_only_own_tasks(self, auth_client, other_user, task, db):
        Task.objects.create(user=other_user, title="Other Task")
        response = auth_client.get(reverse("task_list"))
        content = response.content.decode()
        assert "Test Task" in content
        assert "Other Task" not in content


class TestTaskCreateView:
    def test_create(self, auth_client, user):
        response = auth_client.post(
            reverse("task_create"),
            {"title": "New Task", "priority": "high", "status": "todo"},
        )
        assert response.status_code == 302
        assert Task.objects.filter(title="New Task", user=user).exists()


class TestTaskUpdateView:
    def test_update(self, auth_client, task):
        auth_client.post(
            reverse("task_update", args=[task.pk]),
            {"title": "Updated", "priority": "low", "status": "done"},
        )
        task.refresh_from_db()
        assert task.title == "Updated"

    def test_other_user_gets_404(self, client, other_user, task):
        client.login(username="otheruser", password="testpass123")
        response = client.post(
            reverse("task_update", args=[task.pk]),
            {"title": "Hacked", "priority": "low", "status": "done"},
        )
        assert response.status_code == 404
        task.refresh_from_db()
        assert task.title == "Test Task"


class TestTaskDeleteView:
    def test_delete(self, auth_client, task):
        auth_client.post(reverse("task_delete", args=[task.pk]))
        assert not Task.objects.filter(pk=task.pk).exists()

    def test_other_user_gets_404(self, client, other_user, task):
        client.login(username="otheruser", password="testpass123")
        response = client.post(reverse("task_delete", args=[task.pk]))
        assert response.status_code == 404
        assert Task.objects.filter(pk=task.pk).exists()


class TestTaskFilterView:
    def test_filter_by_status(self, auth_client, user, db):
        Task.objects.create(user=user, title="Done Task", status=Task.Status.DONE)
        Task.objects.create(user=user, title="Todo Task", status=Task.Status.TODO)
        response = auth_client.get(reverse("task_list") + "?status=done")
        content = response.content.decode()
        assert "Done Task" in content
        assert "Todo Task" not in content

    def test_filter_by_priority(self, auth_client, user, db):
        Task.objects.create(user=user, title="High Task", priority=Task.Priority.HIGH)
        Task.objects.create(user=user, title="Low Task", priority=Task.Priority.LOW)
        response = auth_client.get(reverse("task_list") + "?priority=high")
        content = response.content.decode()
        assert "High Task" in content
        assert "Low Task" not in content

    def test_search(self, auth_client, user, db):
        Task.objects.create(user=user, title="Find me")
        Task.objects.create(user=user, title="Invisible")
        response = auth_client.get(reverse("task_list") + "?search=Find")
        content = response.content.decode()
        assert "Find me" in content
        assert "Invisible" not in content


class TestSendDeadlineReminders:
    def test_no_tasks_returns_zero(self, db):
        from tasks.tasks import send_deadline_reminders

        result = send_deadline_reminders()
        assert result == 0

    def test_sends_reminder_for_upcoming_task(self, user, db):
        from django.utils import timezone

        from tasks.tasks import send_deadline_reminders

        user.email = "test@example.com"
        user.save()

        Task.objects.create(
            user=user,
            title="Upcoming Task",
            deadline=timezone.now() + timezone.timedelta(hours=12),
            status=Task.Status.TODO,
        )

        result = send_deadline_reminders()
        assert result == 1

    def test_skips_done_tasks(self, user, db):
        from django.utils import timezone

        from tasks.tasks import send_deadline_reminders

        user.email = "test@example.com"
        user.save()

        Task.objects.create(
            user=user,
            title="Done Task",
            deadline=timezone.now() + timezone.timedelta(hours=12),
            status=Task.Status.DONE,
        )

        result = send_deadline_reminders()
        assert result == 0

    def test_skips_user_without_email(self, user, db):
        from django.utils import timezone

        from tasks.tasks import send_deadline_reminders

        Task.objects.create(
            user=user,
            title="Task",
            deadline=timezone.now() + timezone.timedelta(hours=12),
            status=Task.Status.TODO,
        )

        result = send_deadline_reminders()
        assert result == 0


class TestSignUpView:
    def test_signup_auto_login(self, client, db):
        response = client.post(
            reverse("signup"),
            {
                "username": "newuser",
                "email": "new@example.com",
                "password1": "complexpass123",
                "password2": "complexpass123",
            },
        )
        assert response.status_code == 302
        assert response["Location"] == reverse("task_list")
