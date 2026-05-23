from django.db import IntegrityError
from django.test import TestCase

from crm.models import Contact, ContactEmailAddress, ContactPhoneNumber


class ContactStrTest(TestCase):
    def test_str_returns_full_name(self):
        contact = Contact.objects.create(first_name="Anna", last_name="Müller")
        self.assertEqual(str(contact), "Anna Müller")

    def test_str_with_salutation_in_detail(self):
        contact = Contact.objects.create(
            first_name="Hans", last_name="Meier", salutation=Contact.Salutation.HERR
        )
        self.assertEqual(contact.get_salutation_display(), "Herr")
        self.assertEqual(str(contact), "Hans Meier")

    def test_salutation_blank_by_default(self):
        contact = Contact.objects.create(first_name="Alex", last_name="Huber")
        self.assertEqual(contact.salutation, "")


class ContactEmailConstraintTest(TestCase):
    def test_only_one_primary_email_per_contact(self):
        contact = Contact.objects.create(first_name="Max", last_name="Muster")
        ContactEmailAddress.objects.create(contact=contact, email="a@example.com", is_primary=True)
        with self.assertRaises(IntegrityError):
            ContactEmailAddress.objects.create(contact=contact, email="b@example.com", is_primary=True)

    def test_two_contacts_can_each_have_primary_email(self):
        c1 = Contact.objects.create(first_name="A", last_name="A")
        c2 = Contact.objects.create(first_name="B", last_name="B")
        ContactEmailAddress.objects.create(contact=c1, email="a@example.com", is_primary=True)
        ContactEmailAddress.objects.create(contact=c2, email="b@example.com", is_primary=True)


class ContactPhoneConstraintTest(TestCase):
    def test_only_one_primary_phone_per_contact(self):
        contact = Contact.objects.create(first_name="Max", last_name="Muster")
        ContactPhoneNumber.objects.create(contact=contact, phone_number="+41 79 000 0000", is_primary=True)
        with self.assertRaises(IntegrityError):
            ContactPhoneNumber.objects.create(contact=contact, phone_number="+41 79 000 0001", is_primary=True)
