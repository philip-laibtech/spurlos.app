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



class CompanyPhoneConstraintTest(TestCase):
    def test_only_one_primary_phone_per_company(self):
        company = _make_company()
        CompanyPhoneNumber.objects.create(company=company, phone_number="+41 44 000 0000", is_primary=True)
        with self.assertRaises(IntegrityError):
            CompanyPhoneNumber.objects.create(company=company, phone_number="+41 44 000 0001", is_primary=True)
