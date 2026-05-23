from django.core.exceptions import ValidationError
from django.test import TestCase

from crm.models import Address, Company, CompanyLocation
from crm.services import create_company, create_company_location, set_company_hq


def _make_address():
    return Address.objects.create(line1="Bahnhofstrasse 1", postal_code="8000", city="Zürich")


def _make_company(name="Acme AG"):
    return Company.objects.create(name=name)


def _make_location(company, name="Office", **kwargs):
    return CompanyLocation.objects.create(
        company=company, address=_make_address(), name=name, **kwargs
    )


class SetCompanyHQTest(TestCase):
    def test_sets_hq_location_on_company(self):
        company = _make_company()
        location = _make_location(company)
        set_company_hq(company, location)
        company.refresh_from_db()
        self.assertEqual(company.hq_location_id, location.pk)

    def test_marks_location_as_headquarters(self):
        company = _make_company()
        location = _make_location(company)
        set_company_hq(company, location)
        location.refresh_from_db()
        self.assertTrue(location.is_headquarters)

    def test_unsets_old_hq(self):
        company = _make_company()
        old_hq = _make_location(company, name="Old HQ", is_headquarters=True)
        company.hq_location = old_hq
        company.save()
        new_hq = _make_location(company, name="New HQ")
        set_company_hq(company, new_hq)
        old_hq.refresh_from_db()
        self.assertFalse(old_hq.is_headquarters)

    def test_rejects_location_from_other_company(self):
        company_a = _make_company("Company A")
        company_b = _make_company("Company B")
        location_b = _make_location(company_b)
        with self.assertRaises(ValidationError):
            set_company_hq(company_a, location_b)


class CreateCompanyTest(TestCase):
    def test_creates_company(self):
        company = create_company("New Co")
        self.assertIsNotNone(company.pk)
        self.assertEqual(company.name, "New Co")
