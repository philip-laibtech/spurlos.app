from django.core.exceptions import ValidationError
from django.test import TestCase

from crm.models import Company, Contact
from projects.models import Project
from projects.services import archive_project, create_project, restore_project, update_project


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
