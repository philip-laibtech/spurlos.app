import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase

from crm.models import Company
from projects.models import Project
from tasks.models import Task


class TaskModelTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Acme Corp")
        self.project = Project.objects.create(title="Alpha Project", company=self.company)

    def test_str_with_task_id(self):
        task = Task(task_id="TSK-2026-0001", title="Call customer", project=self.project)
        self.assertEqual(str(task), "TSK-2026-0001 - Call customer")

    def test_str_without_task_id(self):
        task = Task(title="Send invoice", project=self.project)
        self.assertEqual(str(task), "Send invoice")

    def test_requires_project(self):
        task = Task(title="No project")
        with self.assertRaises(ValidationError):
            task.full_clean()

    def test_requires_title(self):
        task = Task(project=self.project, title="")
        with self.assertRaises(ValidationError):
            task.full_clean()

    def test_allows_assigned_user_blank(self):
        task = Task(title="Unassigned", project=self.project)
        task.full_clean()  # should not raise

    def test_allows_due_date_blank(self):
        task = Task(title="No due date", project=self.project)
        task.full_clean()  # should not raise

    def test_allows_past_due_date(self):
        task = Task(title="Past task", project=self.project, due_date=datetime.date(2020, 1, 1))
        task.full_clean()  # should not raise

    def test_default_status_is_open(self):
        task = Task(title="New task", project=self.project)
        self.assertEqual(task.status, Task.Status.OPEN)

    def test_default_priority_is_normal(self):
        task = Task(title="New task", project=self.project)
        self.assertEqual(task.priority, Task.Priority.NORMAL)
