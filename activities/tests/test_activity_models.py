from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

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


class ActivityStrTest(TestCase):
    def test_str_with_activity_id(self):
        from activities.services import create_activity
        company = _make_company()
        activity = create_activity(company=company, title="Called Sarah", activity_id="ACT-2026-0001")
        self.assertEqual(str(activity), "ACT-2026-0001 - Called Sarah")

    def test_str_without_activity_id(self):
        from activities.services import create_activity
        company = _make_company()
        activity = create_activity(company=company, title="Called Sarah")
        activity.activity_id = ""
        self.assertEqual(str(activity), "Called Sarah")


class ActivityValidationTest(TestCase):
    def test_requires_company(self):
        from activities.models import Activity
        activity = Activity(title="Test", occurred_at=timezone.now())
        with self.assertRaises(ValidationError):
            activity.full_clean()

    def test_requires_title(self):
        from activities.models import Activity
        company = _make_company()
        activity = Activity(company=company, occurred_at=timezone.now())
        with self.assertRaises(ValidationError):
            activity.full_clean()

    def test_allows_company_only(self):
        from activities.models import Activity
        company = _make_company()
        activity = Activity(company=company, title="Test", occurred_at=timezone.now())
        activity.full_clean()  # should not raise

    def test_allows_company_with_matching_contact(self):
        from activities.models import Activity
        company = _make_company()
        contact = _make_contact(company=company)
        activity = Activity(company=company, contact=contact, title="Test", occurred_at=timezone.now())
        activity.full_clean()  # should not raise

    def test_rejects_contact_from_different_company(self):
        from activities.models import Activity
        company1 = _make_company(name="Alpha")
        company2 = _make_company(name="Beta")
        contact = _make_contact(company=company1)
        activity = Activity(company=company2, contact=contact, title="Test", occurred_at=timezone.now())
        with self.assertRaises(ValidationError):
            activity.full_clean()

    def test_allows_matching_project(self):
        from activities.models import Activity
        company = _make_company()
        project = _make_project(company=company)
        activity = Activity(company=company, project=project, title="Test", occurred_at=timezone.now())
        activity.full_clean()  # should not raise

    def test_rejects_project_from_different_company(self):
        from activities.models import Activity
        company1 = _make_company(name="Alpha")
        company2 = _make_company(name="Beta")
        project = _make_project(company=company2)
        activity = Activity(company=company1, project=project, title="Test", occurred_at=timezone.now())
        with self.assertRaises(ValidationError):
            activity.full_clean()

    def test_no_task_field(self):
        from activities.models import Activity
        self.assertFalse(hasattr(Activity, "task"))
        field_names = [f.name for f in Activity._meta.get_fields()]
        self.assertNotIn("task", field_names)
