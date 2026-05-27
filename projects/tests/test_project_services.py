import re

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from crm.models import Company, Contact
from projects.models import Project
from projects.services import (
    archive_project,
    create_project,
    generate_project_number,
    restore_project,
    update_project,
)


class ProjectServiceTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Acme Corp")
        self.other_company = Company.objects.create(name="Other Corp")
        self.contact = Contact.objects.create(
            first_name="Jane", last_name="Doe", company=self.company
        )

    def test_create_project_with_company_and_title(self):
        project = create_project(company=self.company, title="Project A")
        self.assertEqual(project.title, "Project A")
        self.assertEqual(project.company, self.company)
        self.assertIsNone(project.contact)
        self.assertIsNotNone(project.pk)

    def test_create_project_with_contact(self):
        project = create_project(company=self.company, title="Project B", contact=self.contact)
        self.assertEqual(project.contact, self.contact)

    def test_create_project_rejects_invalid_contact_company(self):
        other_contact = Contact.objects.create(
            first_name="Bob", last_name="Smith", company=self.other_company
        )
        with self.assertRaises(ValidationError):
            create_project(company=self.company, title="Bad", contact=other_contact)

    def test_update_project_fields(self):
        project = create_project(company=self.company, title="Original")
        updated = update_project(project, title="Updated", contact=self.contact)
        self.assertEqual(updated.title, "Updated")
        self.assertEqual(updated.contact, self.contact)

    def test_archive_project_sets_deleted_at(self):
        project = create_project(company=self.company, title="To Archive")
        archive_project(project)
        project.refresh_from_db()
        self.assertIsNotNone(project.deleted_at)

    def test_restore_project_clears_deleted_at(self):
        project = create_project(company=self.company, title="To Restore")
        archive_project(project)
        restore_project(project)
        project.refresh_from_db()
        self.assertIsNone(project.deleted_at)

    def test_create_project_auto_generates_project_number(self):
        project = create_project(company=self.company, title="Numbered")
        year = timezone.now().year
        self.assertIsNotNone(project.project_number)
        self.assertTrue(project.project_number.startswith(f"SL{year}"))

    def test_create_project_increments_project_number(self):
        p1 = create_project(company=self.company, title="First")
        p2 = create_project(company=self.company, title="Second")
        num1 = int(p1.project_number[6:])
        num2 = int(p2.project_number[6:])
        self.assertEqual(num2, num1 + 1)

    def test_create_project_preserves_manual_project_number(self):
        project = create_project(company=self.company, title="Manual", project_number="SL-CUSTOM-001")
        self.assertEqual(project.project_number, "SL-CUSTOM-001")

    def test_create_project_default_status_is_planned(self):
        project = create_project(company=self.company, title="New")
        self.assertEqual(project.status, Project.Status.PLANNED)

    def test_create_project_with_explicit_status(self):
        project = create_project(company=self.company, title="Active", status=Project.Status.ACTIVE)
        self.assertEqual(project.status, Project.Status.ACTIVE)

    def test_update_project_status(self):
        project = create_project(company=self.company, title="Proj")
        updated = update_project(project, status=Project.Status.COMPLETED)
        self.assertEqual(updated.status, Project.Status.COMPLETED)

    def test_generate_project_number_format(self):
        year = timezone.now().year
        number = generate_project_number()
        self.assertRegex(number, rf"^SL{year}\d{{5}}$")
