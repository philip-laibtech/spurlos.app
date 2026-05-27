import io

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone

from crm.models import Company
from documents.services import (
    archive_document,
    create_document,
    generate_document_id,
    restore_document,
    validate_uploaded_document_file,
)


def _make_company(name="Acme AG"):
    return Company.objects.create(name=name)


def _make_file(name="test.pdf", size=1024, content_type="application/pdf"):
    content = b"x" * size
    f = SimpleUploadedFile(name, content, content_type=content_type)
    return f


class GenerateDocumentIdTest(TestCase):
    def test_returns_correct_format(self):
        doc_id = generate_document_id()
        year = timezone.now().year
        self.assertTrue(doc_id.startswith(f"DOC-{year}-"))
        self.assertEqual(doc_id, f"DOC-{year}-0001")

    def test_increments_sequence(self):
        year = timezone.now().year
        company = _make_company()
        create_document(file=_make_file(), company=company)
        doc_id = generate_document_id()
        self.assertEqual(doc_id, f"DOC-{year}-0002")


class CreateDocumentTest(TestCase):
    def test_creates_document_with_file_and_company(self):
        company = _make_company()
        doc = create_document(file=_make_file(), company=company)
        self.assertIsNotNone(doc.pk)
        self.assertEqual(doc.company, company)

    def test_auto_generates_document_id_when_blank(self):
        company = _make_company()
        doc = create_document(file=_make_file(), company=company)
        year = timezone.now().year
        self.assertTrue(doc.document_id.startswith(f"DOC-{year}-"))

    def test_preserves_manual_document_id(self):
        company = _make_company()
        doc = create_document(file=_make_file(), company=company, document_id="DOC-CUSTOM-001")
        self.assertEqual(doc.document_id, "DOC-CUSTOM-001")

    def test_stores_original_filename_and_file_size(self):
        company = _make_company()
        f = _make_file(name="report.pdf", size=2048)
        doc = create_document(file=f, company=company)
        self.assertEqual(doc.original_filename, "report.pdf")
        self.assertEqual(doc.file_size, 2048)

    def test_stores_mime_type(self):
        company = _make_company()
        f = _make_file(name="report.pdf", content_type="application/pdf")
        doc = create_document(file=f, company=company)
        self.assertEqual(doc.mime_type, "application/pdf")

    def test_defaults_title_to_original_filename(self):
        company = _make_company()
        f = _make_file(name="my_report.pdf")
        doc = create_document(file=f, company=company)
        self.assertEqual(doc.title, "my_report.pdf")

    def test_uses_provided_title(self):
        company = _make_company()
        f = _make_file(name="my_report.pdf")
        doc = create_document(file=f, title="Annual Report", company=company)
        self.assertEqual(doc.title, "Annual Report")


class ValidateUploadedDocumentFileTest(TestCase):
    def test_rejects_blocked_extension(self):
        f = SimpleUploadedFile("malware.exe", b"x" * 100, content_type="application/octet-stream")
        with self.assertRaises(ValidationError):
            validate_uploaded_document_file(f)

    def test_rejects_too_large_file(self):
        f = SimpleUploadedFile("big.pdf", b"x" * (11 * 1024 * 1024), content_type="application/pdf")
        with self.assertRaises(ValidationError):
            validate_uploaded_document_file(f)

    def test_accepts_valid_pdf(self):
        f = _make_file(name="ok.pdf")
        validate_uploaded_document_file(f)  # should not raise


class ArchiveRestoreDocumentTest(TestCase):
    def _make_doc(self):
        company = _make_company()
        return create_document(file=_make_file(), company=company)

    def test_archive_sets_deleted_at(self):
        doc = self._make_doc()
        self.assertIsNone(doc.deleted_at)
        archive_document(doc)
        doc.refresh_from_db()
        self.assertIsNotNone(doc.deleted_at)

    def test_restore_clears_deleted_at(self):
        doc = self._make_doc()
        archive_document(doc)
        restore_document(doc)
        doc.refresh_from_db()
        self.assertIsNone(doc.deleted_at)
