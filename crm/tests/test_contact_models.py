from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from crm.models import Address, Company, CompanyLocation, Contact, ContactEmailAddress, ContactPhoneNumber


def _make_company(name="Acme AG"):
    return Company.objects.create(name=name)


def _make_location(company, name="Main Office"):
    address = Address.objects.create(line1="Teststrasse 1", postal_code="8000", city="Zürich")
    return CompanyLocation.objects.create(company=company, address=address, name=name)


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


class ContactWorkLocationTest(TestCase):
    def test_work_location_must_belong_to_same_company(self):
        company_a = _make_company("Company A")
        company_b = _make_company("Company B")
        location_b = _make_location(company_b, "B Office")
        contact = Contact(first_name="Max", last_name="Muster", company=company_a, work_location=location_b)
        with self.assertRaises(ValidationError):
            contact.full_clean()

    def test_work_location_from_same_company_is_valid(self):
        company = _make_company()
        location = _make_location(company)
        contact = Contact(first_name="Max", last_name="Muster", company=company, work_location=location)
        contact.full_clean()  # should not raise

    def test_work_location_without_company_is_valid(self):
        company = _make_company()
        location = _make_location(company)
        contact = Contact(first_name="Max", last_name="Muster", work_location=location)
        contact.full_clean()  # no company set, no cross-check needed

    def test_linkedin_url_stored(self):
        contact = Contact.objects.create(
            first_name="Max", last_name="Muster",
            linkedin_url="https://linkedin.com/in/max-muster"
        )
        contact.refresh_from_db()
        self.assertEqual(contact.linkedin_url, "https://linkedin.com/in/max-muster")
