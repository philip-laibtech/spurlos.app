import uuid

from django.core.exceptions import ValidationError
from django.test import TestCase

from crm.models import Company, Contact
from documents.models import Document
from projects.models import Project
from tasks.models import Task


def _make_company(name="Acme AG"):
    return Company.objects.create(name=name)


def _make_contact(company=None, first_name="Jane", last_name="Doe"):
    return Contact.objects.create(company=company, first_name=first_name, last_name=last_name)


def _make_project(company, title="Project Alpha"):
    return Project.objects.create(title=title, company=company)


def _make_task(project, title="Task One"):
    task = Task(project=project, title=title, task_id=f"TASK-{project.pk}-{uuid.uuid4().hex[:6]}")
    task.save()
    return task


def _make_document(**kwargs):
    defaults = {
        "title": "Test Doc",
        "file": "documents/2026/01/test.pdf",
        "document_id": "DOC-2026-0001",
    }
    defaults.update(kwargs)
    doc = Document(**defaults)
    return doc


class DocumentStrTest(TestCase):
    def test_str_with_document_id(self):
        company = _make_company()
        doc = _make_document(company=company, document_id="DOC-2026-0001", title="Contract.pdf")
        self.assertEqual(str(doc), "DOC-2026-0001 - Contract.pdf")

    def test_str_without_document_id(self):
        company = _make_company()
        doc = _make_document(company=company, document_id="", title="My File")
        self.assertEqual(str(doc), "My File")


class DocumentValidationTest(TestCase):
    def test_rejects_no_linked_relation(self):
        doc = _make_document()
        with self.assertRaises(ValidationError):
            doc.full_clean()

    def test_allows_company_only(self):
        company = _make_company()
        doc = _make_document(company=company)
        doc.full_clean()  # should not raise

    def test_allows_project_only(self):
        company = _make_company()
        project = _make_project(company)
        doc = _make_document(project=project)
        doc.full_clean()  # should not raise

    def test_rejects_task_project_mismatch(self):
        company = _make_company()
        project_a = _make_project(company, title="Project A")
        project_b = _make_project(company, title="Project B")
        task = _make_task(project_a)
        doc = _make_document(task=task, project=project_b)
        with self.assertRaises(ValidationError):
            doc.full_clean()

    def test_rejects_project_company_mismatch(self):
        company_a = _make_company("Company A")
        company_b = _make_company("Company B")
        project = _make_project(company_a)
        doc = _make_document(project=project, company=company_b)
        with self.assertRaises(ValidationError):
            doc.full_clean()

    def test_rejects_contact_company_mismatch(self):
        company_a = _make_company("Company A")
        company_b = _make_company("Company B")
        contact = _make_contact(company=company_a)
        doc = _make_document(contact=contact, company=company_b)
        with self.assertRaises(ValidationError):
            doc.full_clean()
