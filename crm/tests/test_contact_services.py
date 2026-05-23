from django.core.exceptions import ValidationError
from django.test import TestCase

from crm.models import Contact, ContactEmailAddress, ContactPhoneNumber
from crm.services import (
    add_contact_email,
    add_contact_phone_number,
    create_contact,
    set_primary_contact_email,
    set_primary_contact_phone,
)


def _make_contact(**kwargs):
    defaults = {"first_name": "Max", "last_name": "Muster"}
    defaults.update(kwargs)
    return Contact.objects.create(**defaults)


class SetPrimaryContactEmailTest(TestCase):
    def test_sets_primary_email(self):
        contact = _make_contact()
        email = ContactEmailAddress.objects.create(contact=contact, email="a@example.com")
        set_primary_contact_email(contact, email)
        email.refresh_from_db()
        self.assertTrue(email.is_primary)

    def test_unsets_other_primary_emails(self):
        contact = _make_contact()
        old_primary = ContactEmailAddress.objects.create(
            contact=contact, email="old@example.com", is_primary=True
        )
        new_primary = ContactEmailAddress.objects.create(
            contact=contact, email="new@example.com", is_primary=False
        )
        set_primary_contact_email(contact, new_primary)
        old_primary.refresh_from_db()
        self.assertFalse(old_primary.is_primary)

    def test_rejects_email_from_other_contact(self):
        c1 = _make_contact(first_name="A", last_name="A")
        c2 = _make_contact(first_name="B", last_name="B")
        email = ContactEmailAddress.objects.create(contact=c2, email="x@example.com")
        with self.assertRaises(ValidationError):
            set_primary_contact_email(c1, email)


class SetPrimaryContactPhoneTest(TestCase):
    def test_unsets_other_primary_phones(self):
        contact = _make_contact()
        old_primary = ContactPhoneNumber.objects.create(
            contact=contact, phone_number="+41 79 000 0000", is_primary=True
        )
        new_primary = ContactPhoneNumber.objects.create(
            contact=contact, phone_number="+41 79 000 0001", is_primary=False
        )
        set_primary_contact_phone(contact, new_primary)
        old_primary.refresh_from_db()
        self.assertFalse(old_primary.is_primary)

    def test_rejects_phone_from_other_contact(self):
        c1 = _make_contact(first_name="A", last_name="A")
        c2 = _make_contact(first_name="B", last_name="B")
        phone = ContactPhoneNumber.objects.create(contact=c2, phone_number="+41 79 111 1111")
        with self.assertRaises(ValidationError):
            set_primary_contact_phone(c1, phone)


class CreateContactTest(TestCase):
    def test_creates_contact(self):
        contact = create_contact("Anna", "Meier")
        self.assertIsNotNone(contact.pk)

    def test_creates_contact_with_salutation(self):
        contact = create_contact("Anna", "Meier", salutation=Contact.Salutation.FRAU)
        self.assertEqual(contact.salutation, Contact.Salutation.FRAU)
