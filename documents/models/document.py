import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


def _document_upload_path(instance, filename):
    safe_name = os.path.basename(filename)
    safe_name = "".join(c if (c.isalnum() or c in "._-") else "_" for c in safe_name)
    now = timezone.now()
    return f"documents/{now.year}/{now.month:02d}/{safe_name}"


class Document(models.Model):
    document_id = models.CharField(max_length=50, unique=True, blank=True, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to=_document_upload_path)
    original_filename = models.CharField(max_length=255, blank=True)
    file_size = models.PositiveBigIntegerField(null=True, blank=True)
    mime_type = models.CharField(max_length=120, blank=True)

    company = models.ForeignKey(
        "crm.Company",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents",
    )
    contact = models.ForeignKey(
        "crm.Contact",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents",
    )
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents",
    )
    task = models.ForeignKey(
        "tasks.Task",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents",
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_documents",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["document_id"]),
            models.Index(fields=["title"]),
            models.Index(fields=["company"]),
            models.Index(fields=["contact"]),
            models.Index(fields=["project"]),
            models.Index(fields=["task"]),
            models.Index(fields=["uploaded_by"]),
            models.Index(fields=["mime_type"]),
            models.Index(fields=["deleted_at"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        if self.document_id:
            return f"{self.document_id} - {self.title}"
        return self.title

    def clean(self):
        if not any([self.company_id, self.contact_id, self.project_id, self.task_id]):
            raise ValidationError(
                "A document must be linked to at least one of: company, contact, project, or task."
            )
        if self.task_id and self.project_id:
            if self.task.project_id != self.project_id:
                raise ValidationError("The selected task does not belong to the selected project.")
        if self.project_id and self.company_id:
            if self.project.company_id != self.company_id:
                raise ValidationError("The selected project does not belong to the selected company.")
        if self.contact_id and self.company_id:
            if self.contact.company_id != self.company_id:
                raise ValidationError("The selected contact does not belong to the selected company.")
