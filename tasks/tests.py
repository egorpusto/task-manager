from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from .models import Tag, Task


class TagModelTest(TestCase):
    def test_tag_str(self):
        tag = Tag.objects.create(name="urgent")
        self.assertEqual(str(tag), "urgent")

    def test_tag_unique(self):
        Tag.objects.create(name="work")
        with self.assertRaises(Exception):
            Tag.objects.create(name="work")


class TaskModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

    def test_task_str(self):
        task = Task.objects.create(user=self.user, title="Test Task")
        self.assertEqual(str(task), "Test Task")

    def test_task_default_status(self):
        task = Task.objects.create(user=self.user, title="Test Task")
        self.assertEqual(task.status, "todo")

    def test_task_default_priority(self):
        task = Task.objects.create(user=self.user, title="Test Task")
        self.assertEqual(task.priority, "medium")

    def test_task_ordering(self):
        Task.objects.create(user=self.user, title="First")
        task2 = Task.objects.create(user=self.user, title="Second")
        tasks = Task.objects.all()
        self.assertEqual(tasks[0], task2)


class TaskViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="otheruser", password="testpass123"
        )
        self.task = Task.objects.create(
            user=self.user, title="Test Task", status="todo"
        )

    def test_task_list_requires_login(self):
        response = self.client.get(reverse("task_list"))
        self.assertRedirects(response, "/accounts/login/?next=/")

    def test_task_list_authenticated(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("task_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Task")

    def test_task_list_only_own_tasks(self):
        Task.objects.create(user=self.other_user, title="Other Task")
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("task_list"))
        self.assertContains(response, "Test Task")
        self.assertNotContains(response, "Other Task")

    def test_task_create(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("task_create"),
            {
                "title": "New Task",
                "description": "Some description",
                "priority": "high",
                "status": "todo",
            },
        )
        self.assertRedirects(response, reverse("task_list"))
        self.assertTrue(Task.objects.filter(title="New Task", user=self.user).exists())

    def test_task_update(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("task_update", args=[self.task.pk]),
            {
                "title": "Updated Task",
                "priority": "low",
                "status": "done",
            },
        )
        self.assertRedirects(response, reverse("task_list"))
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, "Updated Task")

    def test_task_update_other_user_forbidden(self):
        self.client.login(username="otheruser", password="testpass123")
        response = self.client.post(
            reverse("task_update", args=[self.task.pk]),
            {
                "title": "Hacked",
                "priority": "low",
                "status": "done",
            },
        )
        self.assertIn(response.status_code, [403, 404])
        self.task.refresh_from_db()
        self.assertNotEqual(self.task.title, "Hacked")

    def test_task_delete(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(reverse("task_delete", args=[self.task.pk]))
        self.assertRedirects(response, reverse("task_list"))
        self.assertFalse(Task.objects.filter(pk=self.task.pk).exists())

    def test_task_delete_other_user_forbidden(self):
        self.client.login(username="otheruser", password="testpass123")
        response = self.client.post(reverse("task_delete", args=[self.task.pk]))
        self.assertIn(response.status_code, [403, 404])
        self.assertTrue(Task.objects.filter(pk=self.task.pk).exists())


class TaskFilterTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.client.login(username="testuser", password="testpass123")
        Task.objects.create(
            user=self.user, title="High Task", priority="high", status="todo"
        )
        Task.objects.create(
            user=self.user, title="Low Task", priority="low", status="done"
        )

    def test_filter_by_status(self):
        response = self.client.get(reverse("task_list") + "?status=done")
        self.assertContains(response, "Low Task")
        self.assertNotContains(response, "High Task")

    def test_filter_by_priority(self):
        response = self.client.get(reverse("task_list") + "?priority=high")
        self.assertContains(response, "High Task")
        self.assertNotContains(response, "Low Task")

    def test_search_by_title(self):
        response = self.client.get(reverse("task_list") + "?search=High")
        self.assertContains(response, "High Task")
        self.assertNotContains(response, "Low Task")
