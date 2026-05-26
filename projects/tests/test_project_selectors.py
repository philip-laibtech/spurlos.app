from django.test import TestCase

from crm.models import Company, Contact
from projects.models import Project
from projects.selectors import (
    get_project_queryset,
    get_projects_for_company,
    get_projects_for_contact,
    search_projects,
)
from projects.services import archive_project, create_project


class ProjectSelectorTests(TestCase):
    def setUp(self):
        self.company_a = Company.objects.create(name="Acme Corp")
        self.company_b = Company.objects.create(name="Beta Ltd")
        self.contact = Contact.objects.create(
            first_name="Jane", last_name="Doe", company=self.company_a
        )
        self.project_a = create_project(company=self.company_a, title="Alpha Project", contact=self.contact)
        self.project_b = create_project(company=self.company_b, title="Beta Project")

    def test_queryset_excludes_soft_deleted(self):
        archive_project(self.project_a)
        qs = get_project_queryset()
        self.assertNotIn(self.project_a, qs)
        self.assertIn(self.project_b, qs)

    def test_get_projects_for_company(self):
        qs = get_projects_for_company(self.company_a)
        self.assertIn(self.project_a, qs)
        self.assertNotIn(self.project_b, qs)

    def test_get_projects_for_contact(self):
        qs = get_projects_for_contact(self.contact)
        self.assertIn(self.project_a, qs)
        self.assertNotIn(self.project_b, qs)

    def test_search_by_title(self):
        qs = search_projects("Alpha")
        self.assertIn(self.project_a, qs)
        self.assertNotIn(self.project_b, qs)

    def test_search_by_company_name(self):
        qs = search_projects("Beta")
        self.assertIn(self.project_b, qs)
        self.assertNotIn(self.project_a, qs)

    def test_search_by_contact_name(self):
        qs = search_projects("Jane")
        self.assertIn(self.project_a, qs)
