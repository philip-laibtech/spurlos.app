import os

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.text import get_valid_filename

from documents.models import Document

ALLOWED_DOCUMENT_EXTENSIONS = {
    "pdf", "doc", "docx", "xls", "xlsx", "csv", "txt", "png", "jpg", "jpeg",
}

MAX_DOCUMENT_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


def generate_document_id() -> str:
    # TODO: replace with a high-concurrency-safe sequence if needed (e.g. database sequence or Redis counter)
    year = timezone.now().year
    prefix = f"DOC-{year}-"
    latest = (
        Document.objects.filter(document_id__startswith=prefix)
        .order_by("-document_id")
        .values_list("document_id", flat=True)
        .first()
    )
    if latest:
        try:
            last_number = int(latest.split("-")[-1])
        except (ValueError, IndexError):
            last_number = 0
        next_number = last_number + 1
    else:
        next_number = 1
    return f"{prefix}{next_number:04d}"


def get_safe_upload_filename(filename: str) -> str:
    name = os.path.basename(filename)
    return get_valid_filename(name)


def validate_uploaded_document_file(uploaded_file) -> None:
    # TODO: add virus scanning before handling untrusted production uploads at scale
    if uploaded_file.size > MAX_DOCUMENT_FILE_SIZE_BYTES:
        max_mb = MAX_DOCUMENT_FILE_SIZE_BYTES // (1024 * 1024)
        raise ValidationError(f"File size must not exceed {max_mb} MB.")
    ext = uploaded_file.name.rsplit(".", 1)[-1].lower() if "." in uploaded_file.name else ""
    if ext not in ALLOWED_DOCUMENT_EXTENSIONS:
        raise ValidationError(
            f"File type '.{ext}' is not allowed. "
            f"Allowed types: {', '.join(sorted(ALLOWED_DOCUMENT_EXTENSIONS))}."
        )


def create_document(
    file,
    title: str = "",
    description: str = "",
    company=None,
    contact=None,
    project=None,
    task=None,
    uploaded_by=None,
    document_id: str = "",
) -> Document:
    validate_uploaded_document_file(file)

    original_filename = get_safe_upload_filename(file.name)

    if not title:
        title = original_filename

    if not document_id:
        document_id = generate_document_id()

    doc = Document(
        document_id=document_id,
        title=title,
        description=description,
        file=file,
        original_filename=original_filename,
        file_size=file.size,
        mime_type=getattr(file, "content_type", ""),
        company=company,
        contact=contact,
        project=project,
        task=task,
        uploaded_by=uploaded_by,
    )
    doc.full_clean()
    doc.save()
    return doc


ALLOWED_UPDATE_FIELDS = {"title", "description", "company", "contact", "project", "task"}


def update_document(document: Document, **data) -> Document:
    for field, value in data.items():
        if field in ALLOWED_UPDATE_FIELDS:
            setattr(document, field, value)
    document.full_clean()
    document.save()
    return document


def archive_document(document: Document) -> Document:
    document.deleted_at = timezone.now()
    document.save(update_fields=["deleted_at", "updated_at"])
    return document


def restore_document(document: Document) -> Document:
    document.deleted_at = None
    document.save(update_fields=["deleted_at", "updated_at"])
    return document
