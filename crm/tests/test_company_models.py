from django.db import IntegrityError
from django.test import TestCase

from crm.models import Address, Company, CompanyLocation, CompanyPhoneNumber


def _make_address(**kwargs):
    defaults = {"line1": "Teststrasse 1", "postal_code": "8000", "city": "Zürich"}
    defaults.update(kwargs)
    return Address.objects.create(**defaults)


def _make_company(**kwargs):
    defaults = {"name": "Acme AG"}
    defaults.update(kwargs)
    return Company.objects.create(**defaults)


class CompanyStrTest(TestCase):
    def test_str(self):
        company = _make_company(name="Spurlos GmbH")
        self.assertEqual(str(company), "Spurlos GmbH")


class CompanyLocationStrTest(TestCase):
    def test_str(self):
        company = _make_company(name="Acme")
        address = _make_address()
        location = CompanyLocation.objects.create(
            company=company, address=address, name="Zürich Office"
        )
        self.assertEqual(str(location), "Acme - Zürich Office")


class CompanyLocationHQConstraintTest(TestCase):
    def test_only_one_hq_per_company(self):
        company = _make_company()
        address = _make_address()
        CompanyLocation.objects.create(
            company=company, address=address, name="HQ", is_headquarters=True
        )
        with self.assertRaises(IntegrityError):
            CompanyLocation.objects.create(
                company=company, address=address, name="HQ2", is_headquarters=True
            )

    def test_two_companies_can_each_have_hq(self):
        c1 = _make_company(name="Company A")
        c2 = _make_company(name="Company B")
        address = _make_address()
        CompanyLocation.objects.create(company=c1, address=address, name="HQ", is_headquarters=True)
        CompanyLocation.objects.create(company=c2, address=address, name="HQ", is_headquarters=True)


class CompanyPhoneConstraintTest(TestCase):
    def test_only_one_primary_phone_per_company(self):
        company = _make_company()
        CompanyPhoneNumber.objects.create(company=company, phone_number="+41 44 000 0000", is_primary=True)
        with self.assertRaises(IntegrityError):
            CompanyPhoneNumber.objects.create(company=company, phone_number="+41 44 000 0001", is_primary=True)
