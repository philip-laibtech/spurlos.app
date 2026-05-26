from django.core.exceptions import ValidationError
from django.db import models


class Project(models.Model):
    title = models.CharField(max_length=255)
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
            models.Index(fields=["title"]),
            models.Index(fields=["company"]),
            models.Index(fields=["contact"]),
            models.Index(fields=["deleted_at"]),
            models.Index(fields=["created_at"]),
        ]

    @property
    def project_number(self):
        return f"SL2026{self.pk:05d}"

    def __str__(self):
        return self.title

    def clean(self):
        if self.contact_id and self.company_id:
            if self.contact.company_id != self.company_id:
                raise ValidationError(
                    "The selected contact does not belong to the selected company."
                )
