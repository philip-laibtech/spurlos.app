from django.test import TestCase

from crm.models import Company
from crm.selectors import get_company_list, search_companies


def _make_company(name="Acme AG", **kwargs):
    return Company.objects.create(name=name, **kwargs)


class CompanyListSelectorTest(TestCase):
    def test_excludes_soft_deleted(self):
        from django.utils import timezone
        _make_company(name="Active Co")
        _make_company(name="Deleted Co", deleted_at=timezone.now())
        qs = get_company_list()
        names = list(qs.values_list("name", flat=True))
        self.assertIn("Active Co", names)
        self.assertNotIn("Deleted Co", names)

    def test_prefetches_relations(self):
        _make_company()
        qs = get_company_list()
        company = qs.first()
        self.assertIsNotNone(company)


class SearchCompaniesTest(TestCase):
    def test_finds_by_name(self):
        _make_company(name="Spurlos GmbH")
        _make_company(name="Other Corp")
        results = search_companies("Spurlos")
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().name, "Spurlos GmbH")

    def test_excludes_soft_deleted(self):
        from django.utils import timezone
        _make_company(name="Spurlos GmbH", deleted_at=timezone.now())
        results = search_companies("Spurlos")
        self.assertEqual(results.count(), 0)
