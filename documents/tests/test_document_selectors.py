from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from crm.models import Company, Contact
from documents.selectors import (
    get_document_queryset,
    get_documents_for_company,
    get_documents_for_contact,
    get_documents_for_project,
    get_documents_for_task,
    search_documents,
)
from documents.services import archive_document, create_document
from projects.models import Project
from tasks.models import Task


def _make_file(name="test.pdf"):
    return SimpleUploadedFile(name, b"x" * 512, content_type="application/pdf")


def _make_company(name="Acme AG"):
    return Company.objects.create(name=name)


def _make_contact(company=None, first_name="Jane", last_name="Doe"):
    return Contact.objects.create(company=company, first_name=first_name, last_name=last_name)


def _make_project(company, title="Project Alpha"):
    return Project.objects.create(title=title, company=company)


import uuid


def _make_task(project, title="Task One"):
    task = Task(project=project, title=title, task_id=f"TASK-{project.pk}-{uuid.uuid4().hex[:6]}")
    task.save()
    return task


class GetDocumentQuerysetTest(TestCase):
    def test_excludes_soft_deleted(self):
        company = _make_company()
        doc = create_document(file=_make_file(), company=company)
        archive_document(doc)
        self.assertNotIn(doc, get_document_queryset())

    def test_includes_active_documents(self):
        company = _make_company()
        doc = create_document(file=_make_file(), company=company)
        self.assertIn(doc, get_document_queryset())


class GetDocumentsForCompanyTest(TestCase):
    def test_returns_only_company_documents(self):
        company_a = _make_company("A")
        company_b = _make_company("B")
        doc_a = create_document(file=_make_file(), company=company_a)
        create_document(file=_make_file(), company=company_b)
        qs = get_documents_for_company(company_a)
        self.assertIn(doc_a, qs)
        self.assertEqual(qs.count(), 1)


class GetDocumentsForContactTest(TestCase):
    def test_returns_only_contact_documents(self):
        contact_a = _make_contact(first_name="Alice")
        contact_b = _make_contact(first_name="Bob")
        doc_a = create_document(file=_make_file(), contact=contact_a)
        create_document(file=_make_file(), contact=contact_b)
        qs = get_documents_for_contact(contact_a)
        self.assertIn(doc_a, qs)
        self.assertEqual(qs.count(), 1)


class GetDocumentsForProjectTest(TestCase):
    def test_returns_only_project_documents(self):
        company = _make_company()
        project_a = _make_project(company, title="A")
        project_b = _make_project(company, title="B")
        doc_a = create_document(file=_make_file(), project=project_a)
        create_document(file=_make_file(), project=project_b)
        qs = get_documents_for_project(project_a)
        self.assertIn(doc_a, qs)
        self.assertEqual(qs.count(), 1)


class GetDocumentsForTaskTest(TestCase):
    def test_returns_only_task_documents(self):
        company = _make_company()
        project = _make_project(company)
        task_a = _make_task(project, title="Task A")
        task_b = _make_task(project, title="Task B")
        doc_a = create_document(file=_make_file(), task=task_a)
        create_document(file=_make_file(), task=task_b)
        qs = get_documents_for_task(task_a)
        self.assertIn(doc_a, qs)
        self.assertEqual(qs.count(), 1)


class SearchDocumentsTest(TestCase):
    def setUp(self):
        self.company = _make_company("Acme AG")
        self.contact = _make_contact(company=self.company, first_name="Alice", last_name="Smith")
        self.project = _make_project(self.company, title="Phoenix Project")
        self.doc = create_document(
            file=_make_file(name="contract.pdf"),
            title="Sales Contract",
            company=self.company,
        )

    def test_search_by_document_id(self):
        results = search_documents(self.doc.document_id)
        self.assertIn(self.doc, results)

    def test_search_by_title(self):
        results = search_documents("Sales")
        self.assertIn(self.doc, results)

    def test_search_by_original_filename(self):
        results = search_documents("contract.pdf")
        self.assertIn(self.doc, results)

    def test_search_by_company_name(self):
        results = search_documents("Acme")
        self.assertIn(self.doc, results)

    def test_search_by_contact_name(self):
        doc2 = create_document(file=_make_file(), contact=self.contact)
        results = search_documents("Alice")
        self.assertIn(doc2, results)

    def test_search_by_project_title(self):
        doc3 = create_document(file=_make_file(), project=self.project)
        results = search_documents("Phoenix")
        self.assertIn(doc3, results)

    def test_empty_query_returns_all(self):
        results = search_documents("")
        self.assertIn(self.doc, results)
