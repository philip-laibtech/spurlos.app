from django.core.exceptions import ValidationError
from django.test import TestCase

from crm.models import Company, Contact
from projects.models import Project


class ProjectModelTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Acme Corp")
        self.other_company = Company.objects.create(name="Other Corp")
        self.contact = Contact.objects.create(
            first_name="Jane", last_name="Doe", company=self.company
        )

    def test_str_returns_title(self):
        project = Project(title="My Project", company=self.company)
        self.assertEqual(str(project), "My Project")

    def test_validation_rejects_contact_from_different_company(self):
        project = Project(
            title="Bad Project",
            company=self.company,
            contact=Contact.objects.create(
                first_name="Bob", last_name="Smith", company=self.other_company
            ),
        )
        with self.assertRaises(ValidationError):
            project.full_clean()

    def test_validation_allows_contact_from_same_company(self):
        project = Project(title="Good Project", company=self.company, contact=self.contact)
        project.full_clean()  # should not raise

    def test_requires_company(self):
        project = Project(title="No Company")
        with self.assertRaises(ValidationError):
            project.full_clean()

    def test_contact_can_be_blank(self):
        project = Project(title="No Contact", company=self.company)
        project.full_clean()  # should not raise

    def test_str_with_project_number(self):
        project = Project(title="Alpha", company=self.company, project_number="SL202600001")
        self.assertEqual(str(project), "SL202600001 - Alpha")

    def test_str_without_project_number(self):
        project = Project(title="Alpha", company=self.company)
        self.assertEqual(str(project), "Alpha")

    def test_default_status_is_planned(self):
        project = Project(title="New", company=self.company)
        self.assertEqual(project.status, Project.Status.PLANNED)
