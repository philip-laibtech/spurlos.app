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


class GenerateActivityIdTest(TestCase):
    def test_format(self):
        from activities.services import generate_activity_id
        activity_id = generate_activity_id()
        year = timezone.now().year
        self.assertTrue(activity_id.startswith(f"ACT-{year}-"))
        suffix = activity_id.split("-")[-1]
        self.assertEqual(len(suffix), 4)
        self.assertEqual(suffix, "0001")

    def test_increments(self):
        from activities.services import create_activity, generate_activity_id
        company = _make_company()
        create_activity(company=company, title="First")
        second_id = generate_activity_id()
        self.assertTrue(second_id.endswith("-0002"))


class CreateActivityTest(TestCase):
    def test_creates_with_company_and_title(self):
        from activities.services import create_activity
        company = _make_company()
        activity = create_activity(company=company, title="Test Call")
        self.assertEqual(activity.title, "Test Call")
        self.assertEqual(activity.company, company)

    def test_autogenerates_activity_id_when_blank(self):
        from activities.services import create_activity
        company = _make_company()
        activity = create_activity(company=company, title="Test")
        self.assertTrue(activity.activity_id.startswith("ACT-"))

    def test_preserves_manual_activity_id(self):
        from activities.services import create_activity
        company = _make_company()
        activity = create_activity(company=company, title="Test", activity_id="ACT-2020-9999")
        self.assertEqual(activity.activity_id, "ACT-2020-9999")

    def test_defaults_occurred_at_when_blank(self):
        from activities.services import create_activity
        company = _make_company()
        before = timezone.now()
        activity = create_activity(company=company, title="Test")
        self.assertGreaterEqual(activity.occurred_at, before)

    def test_contact_is_optional(self):
        from activities.services import create_activity
        company = _make_company()
        activity = create_activity(company=company, title="Test")
        self.assertIsNone(activity.contact)

    def test_rejects_contact_from_different_company(self):
        from django.core.exceptions import ValidationError
        from activities.services import create_activity
        company1 = _make_company(name="Alpha")
        company2 = _make_company(name="Beta")
        contact = _make_contact(company=company1)
        with self.assertRaises(ValidationError):
            create_activity(company=company2, contact=contact, title="Test")


class UpdateActivityTest(TestCase):
    def test_updates_allowed_fields(self):
        from activities.services import create_activity, update_activity
        company = _make_company()
        activity = create_activity(company=company, title="Original")
        update_activity(activity, title="Updated", description="New notes")
        self.assertEqual(activity.title, "Updated")
        self.assertEqual(activity.description, "New notes")


class ArchiveRestoreTest(TestCase):
    def test_archive_sets_deleted_at(self):
        from activities.services import archive_activity, create_activity
        company = _make_company()
        activity = create_activity(company=company, title="Test")
        archive_activity(activity)
        self.assertIsNotNone(activity.deleted_at)

    def test_restore_clears_deleted_at(self):
        from activities.services import archive_activity, create_activity, restore_activity
        company = _make_company()
        activity = create_activity(company=company, title="Test")
        archive_activity(activity)
        restore_activity(activity)
        self.assertIsNone(activity.deleted_at)


class NoSideEffectsTest(TestCase):
    def test_create_does_not_update_contact_fields(self):
        from activities.services import create_activity
        company = _make_company()
        contact = _make_contact(company=company)
        contact_fields_before = {f.name: getattr(contact, f.name) for f in contact._meta.get_fields() if hasattr(f, "attname")}
        create_activity(company=company, contact=contact, title="Test")
        contact.refresh_from_db()
        for field, value in contact_fields_before.items():
            self.assertEqual(getattr(contact, field), value, f"Field {field} changed on contact")

    def test_create_does_not_update_company_fields(self):
        from activities.services import create_activity
        company = _make_company()
        company_fields_before = {f.name: getattr(company, f.name) for f in company._meta.get_fields() if hasattr(f, "attname")}
        create_activity(company=company, title="Test")
        company.refresh_from_db()
        for field, value in company_fields_before.items():
            self.assertEqual(getattr(company, field), value, f"Field {field} changed on company")
