from django.test import TestCase

from crm.models import Contact
from crm.selectors import get_contact_list, search_contacts


def _make_contact(first_name="Max", last_name="Muster", **kwargs):
    return Contact.objects.create(first_name=first_name, last_name=last_name, **kwargs)


class ContactListSelectorTest(TestCase):
    def test_excludes_soft_deleted(self):
        from django.utils import timezone
        _make_contact(first_name="Active", last_name="Contact")
        _make_contact(first_name="Deleted", last_name="Contact", deleted_at=timezone.now())
        qs = get_contact_list()
        names = list(qs.values_list("first_name", flat=True))
        self.assertIn("Active", names)
        self.assertNotIn("Deleted", names)

    def test_ordered_by_last_name(self):
        _make_contact(first_name="B", last_name="Zimmermann")
        _make_contact(first_name="A", last_name="Aebischer")
        qs = get_contact_list()
        self.assertEqual(qs.first().last_name, "Aebischer")


class SearchContactsTest(TestCase):
    def test_finds_by_first_name(self):
        _make_contact(first_name="Martina", last_name="Huber")
        results = search_contacts("Martina")
        self.assertGreaterEqual(results.count(), 1)

    def test_excludes_soft_deleted(self):
        from django.utils import timezone
        _make_contact(first_name="Ghost", last_name="User", deleted_at=timezone.now())
        results = search_contacts("Ghost")
        self.assertEqual(results.count(), 0)
