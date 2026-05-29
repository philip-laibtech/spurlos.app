from django.test import TestCase
from django.utils import timezone

from activities.models import Activity
from activities.selectors import (
    get_activities_by_type,
    get_activities_for_company,
    get_activities_for_contact,
    get_activities_for_project,
    get_activity_queryset,
    search_activities,
)
from activities.services import create_activity
from crm.models import Company, Contact
from projects.models import Project


def _make_company(**kwargs):
    defaults = {"name": "ACME Corp"}
    defaults.update(kwargs)
    return Company.objects.create(**defaults)


def _make_contact(company=None, **kwargs):
    defaults = {"first_name": "Jane", "last_name": "Doe"}
    defaults.update(kwargs)
    if company:
        defaults["company"] = company
    return Contact.objects.create(**defaults)


def _make_project(company, **kwargs):
    defaults = {"title": "Test Project", "company": company}
    defaults.update(kwargs)
    return Project.objects.create(**defaults)


class GetActivityQuerysetTest(TestCase):
    def test_excludes_soft_deleted(self):
        company = _make_company()
        active = create_activity(company=company, title="Active")
        deleted = create_activity(company=company, title="Deleted")
        deleted.deleted_at = timezone.now()
        deleted.save(update_fields=["deleted_at"])
        qs = get_activity_queryset()
        self.assertIn(active, qs)
        self.assertNotIn(deleted, qs)


class GetActivitiesForContactTest(TestCase):
    def test_returns_only_contact_activities(self):
        company = _make_company()
        contact1 = _make_contact(company=company, first_name="Alice")
        contact2 = _make_contact(company=company, first_name="Bob")
        a1 = create_activity(company=company, contact=contact1, title="Alice's Activity")
        a2 = create_activity(company=company, contact=contact2, title="Bob's Activity")
        qs = get_activities_for_contact(contact1)
        self.assertIn(a1, qs)
        self.assertNotIn(a2, qs)


class GetActivitiesForCompanyTest(TestCase):
    def test_returns_only_company_activities(self):
        company1 = _make_company(name="Alpha")
        company2 = _make_company(name="Beta")
        a1 = create_activity(company=company1, title="Alpha Activity")
        a2 = create_activity(company=company2, title="Beta Activity")
        qs = get_activities_for_company(company1)
        self.assertIn(a1, qs)
        self.assertNotIn(a2, qs)


class GetActivitiesForProjectTest(TestCase):
    def test_returns_only_project_activities(self):
        company = _make_company()
        project1 = _make_project(company=company, title="Project A")
        project2 = _make_project(company=company, title="Project B")
        a1 = create_activity(company=company, title="Project A Activity", project=project1)
        a2 = create_activity(company=company, title="Project B Activity", project=project2)
        qs = get_activities_for_project(project1)
        self.assertIn(a1, qs)
        self.assertNotIn(a2, qs)


class GetActivitiesByTypeTest(TestCase):
    def test_filters_by_type(self):
        company = _make_company()
        call = create_activity(company=company, title="A call", activity_type=Activity.ActivityType.CALL)
        email = create_activity(company=company, title="An email", activity_type=Activity.ActivityType.EMAIL)
        qs = get_activities_by_type(Activity.ActivityType.CALL)
        self.assertIn(call, qs)
        self.assertNotIn(email, qs)


class SearchActivitiesTest(TestCase):
    def setUp(self):
        self.company = _make_company(name="Acme Inc")
        self.contact = _make_contact(company=self.company, first_name="Sarah", last_name="Connor")
        self.project = _make_project(company=self.company, title="Terminator Project")
        self.a1 = create_activity(
            company=self.company,
            contact=self.contact,
            title="Called Sarah about pickup",
            activity_id="ACT-2026-0042",
            description="She confirmed the date",
        )
        self.a2 = create_activity(
            company=self.company,
            title="Sent LinkedIn message",
            project=self.project,
        )

    def test_search_by_activity_id(self):
        qs = search_activities("ACT-2026-0042")
        self.assertIn(self.a1, qs)
        self.assertNotIn(self.a2, qs)

    def test_search_by_title(self):
        qs = search_activities("LinkedIn")
        self.assertIn(self.a2, qs)
        self.assertNotIn(self.a1, qs)

    def test_search_by_description(self):
        qs = search_activities("confirmed the date")
        self.assertIn(self.a1, qs)

    def test_search_by_contact_first_name(self):
        qs = search_activities("Sarah")
        self.assertIn(self.a1, qs)

    def test_search_by_contact_last_name(self):
        qs = search_activities("Connor")
        self.assertIn(self.a1, qs)

    def test_search_by_company_name(self):
        qs = search_activities("Acme")
        self.assertIn(self.a1, qs)

    def test_search_by_project_title(self):
        qs = search_activities("Terminator")
        self.assertIn(self.a2, qs)

    def test_empty_query_returns_all(self):
        qs = search_activities("")
        self.assertIn(self.a1, qs)
        self.assertIn(self.a2, qs)
