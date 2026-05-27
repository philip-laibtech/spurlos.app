from django.core.exceptions import ValidationError
from django.db import models


class Project(models.Model):
    class Status(models.TextChoices):
        PLANNED = "planned", "Planned"
        ACTIVE = "active", "Active"
        ON_HOLD = "on_hold", "On Hold"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        ARCHIVED = "archived", "Archived"

    project_number = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
    )
    title = models.CharField(max_length=255)
    status = models.CharField(
        max_length=50,
        choices=Status.choices,
        default=Status.PLANNED,
    )
    company = models.ForeignKey(
        "crm.Company",
        on_delete=models.PROTECT,
        related_name="projects",
    )
    contact = models.ForeignKey(
        "crm.Contact",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="projects",
    )
    assigned_to = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_projects",
    )
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["project_number"]),
            models.Index(fields=["title"]),
            models.Index(fields=["status"]),
            models.Index(fields=["company"]),
            models.Index(fields=["contact"]),
            models.Index(fields=["deleted_at"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        if self.project_number:
            return f"{self.project_number} - {self.title}"
        return self.title

    def clean(self):
        if self.contact_id and self.company_id:
            if self.contact.company_id != self.company_id:
                raise ValidationError(
                    "The selected contact does not belong to the selected company."
                )
