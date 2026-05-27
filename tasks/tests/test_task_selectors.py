from django.test import TestCase

from accounts.models import User
from crm.models import Company
from projects.models import Project
from tasks.selectors import (
    get_task_queryset,
    get_tasks_for_project,
    get_tasks_for_user,
    search_tasks,
)
from tasks.services import archive_task, create_task


class TaskSelectorTests(TestCase):
    def setUp(self):
        self.company_a = Company.objects.create(name="Acme Corp")
        self.company_b = Company.objects.create(name="Beta Ltd")
        self.project_a = Project.objects.create(title="Alpha Project", company=self.company_a)
        self.project_b = Project.objects.create(title="Beta Project", company=self.company_b)
        self.user = User.objects.create_user(email="worker@example.com", password="pass")
        self.task_a = create_task(
            project=self.project_a,
            title="Alpha Task",
            assigned_user=self.user,
            description="Some details about alpha",
            task_id="TSK-2026-0001",
        )
        self.task_b = create_task(
            project=self.project_b,
            title="Beta Task",
            task_id="TSK-2026-0002",
        )

    def test_queryset_excludes_soft_deleted(self):
        archive_task(self.task_a)
        qs = get_task_queryset()
        self.assertNotIn(self.task_a, qs)
        self.assertIn(self.task_b, qs)

    def test_get_tasks_for_project(self):
        qs = get_tasks_for_project(self.project_a)
        self.assertIn(self.task_a, qs)
        self.assertNotIn(self.task_b, qs)

    def test_get_tasks_for_user(self):
        qs = get_tasks_for_user(self.user)
        self.assertIn(self.task_a, qs)
        self.assertNotIn(self.task_b, qs)

    def test_search_by_task_id(self):
        qs = search_tasks("TSK-2026-0001")
        self.assertIn(self.task_a, qs)
        self.assertNotIn(self.task_b, qs)

    def test_search_by_title(self):
        qs = search_tasks("Alpha")
        self.assertIn(self.task_a, qs)
        self.assertNotIn(self.task_b, qs)

    def test_search_by_description(self):
        qs = search_tasks("details about alpha")
        self.assertIn(self.task_a, qs)
        self.assertNotIn(self.task_b, qs)

    def test_search_by_project_title(self):
        qs = search_tasks("Beta Project")
        self.assertIn(self.task_b, qs)
        self.assertNotIn(self.task_a, qs)

    def test_search_by_company_name(self):
        qs = search_tasks("Acme")
        self.assertIn(self.task_a, qs)
        self.assertNotIn(self.task_b, qs)

    def test_search_by_assigned_user_email(self):
        qs = search_tasks("worker@example.com")
        self.assertIn(self.task_a, qs)
        self.assertNotIn(self.task_b, qs)

    def test_empty_query_returns_all(self):
        qs = search_tasks("")
        self.assertIn(self.task_a, qs)
        self.assertIn(self.task_b, qs)
