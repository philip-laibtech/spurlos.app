import datetime
import re

from django.test import TestCase
from django.utils import timezone

from accounts.models import User
from crm.models import Company
from projects.models import Project
from tasks.services import archive_task, create_task, generate_task_id, restore_task, update_task


class TaskServiceTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Acme Corp")
        self.project = Project.objects.create(title="Alpha Project", company=self.company)
        self.user = User.objects.create_user(email="worker@example.com", password="pass")

    def test_generate_task_id_format(self):
        task_id = generate_task_id(self.project)
        year = timezone.now().year
        self.assertRegex(task_id, rf"^TASK{year}{self.project.pk:05d}-\d{{2}}$")

    def test_generate_task_id_increments(self):
        first = generate_task_id(self.project)
        create_task(project=self.project, title="First", task_id=first)
        second = generate_task_id(self.project)
        first_num = int(first.split("-")[-1])
        second_num = int(second.split("-")[-1])
        self.assertEqual(second_num, first_num + 1)

    def test_create_task_with_project_and_title(self):
        task = create_task(project=self.project, title="Do something")
        self.assertEqual(task.title, "Do something")
        self.assertEqual(task.project, self.project)
        self.assertIsNone(task.assigned_user)
        self.assertIsNotNone(task.pk)

    def test_create_task_with_optional_fields(self):
        due = datetime.date(2026, 12, 31)
        task = create_task(
            project=self.project,
            title="Full task",
            assigned_user=self.user,
            description="Some details",
            due_date=due,
        )
        self.assertEqual(task.assigned_user, self.user)
        self.assertEqual(task.description, "Some details")
        self.assertEqual(task.due_date, due)

    def test_create_task_auto_generates_task_id(self):
        task = create_task(project=self.project, title="Auto ID")
        self.assertTrue(task.task_id.startswith("TASK"))

    def test_create_task_preserves_manual_task_id(self):
        task = create_task(project=self.project, title="Manual ID", task_id="TASK2099-9999")
        self.assertEqual(task.task_id, "TASK2099-9999")

    def test_update_task_allowed_fields(self):
        task = create_task(project=self.project, title="Original")
        updated = update_task(task, title="Updated", description="New desc")
        self.assertEqual(updated.title, "Updated")
        self.assertEqual(updated.description, "New desc")

    def test_archive_task_sets_deleted_at(self):
        task = create_task(project=self.project, title="To Archive")
        archive_task(task)
        task.refresh_from_db()
        self.assertIsNotNone(task.deleted_at)

    def test_restore_task_clears_deleted_at(self):
        task = create_task(project=self.project, title="To Restore")
        archive_task(task)
        restore_task(task)
        task.refresh_from_db()
        self.assertIsNone(task.deleted_at)

    def test_create_task_default_status_is_open(self):
        from tasks.models import Task
        task = create_task(project=self.project, title="Status default")
        self.assertEqual(task.status, Task.Status.OPEN)

    def test_create_task_default_priority_is_normal(self):
        from tasks.models import Task
        task = create_task(project=self.project, title="Priority default")
        self.assertEqual(task.priority, Task.Priority.NORMAL)

    def test_create_task_with_explicit_status_and_priority(self):
        from tasks.models import Task
        task = create_task(
            project=self.project,
            title="Explicit",
            status=Task.Status.IN_PROGRESS,
            priority=Task.Priority.HIGH,
        )
        self.assertEqual(task.status, Task.Status.IN_PROGRESS)
        self.assertEqual(task.priority, Task.Priority.HIGH)

    def test_update_task_status_and_priority(self):
        from tasks.models import Task
        task = create_task(project=self.project, title="To update")
        updated = update_task(task, status=Task.Status.DONE, priority=Task.Priority.URGENT)
        self.assertEqual(updated.status, Task.Status.DONE)
        self.assertEqual(updated.priority, Task.Priority.URGENT)
