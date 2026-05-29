from django.test import TestCase

from crm.models import Address, Company, CompanyLocation
from crm.services import create_company, create_company_location


def _make_address():
    return Address.objects.create(line1="Bahnhofstrasse 1", postal_code="8000", city="Zürich")


def _make_company(name="Acme AG"):
    return Company.objects.create(name=name)


class CreateCompanyTest(TestCase):
    def test_creates_company(self):
        company = create_company("New Co")
        self.assertIsNotNone(company.pk)
        self.assertEqual(company.name, "New Co")
