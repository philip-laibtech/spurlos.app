from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Activity(models.Model):
    class ActivityType(models.TextChoices):
        CALL = "call", "Call"
        EMAIL = "email", "Email"
        LINKEDIN = "linkedin", "LinkedIn"
        MEETING = "meeting", "Meeting"
        OTHER = "other", "Other"

    activity_id = models.CharField(max_length=50, unique=True, blank=True, db_index=True)
    company = models.ForeignKey(
        "crm.Company",
        on_delete=models.PROTECT,
        related_name="activities",
    )
    contact = models.ForeignKey(
        "crm.Contact",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activities",
    )
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activities",
    )
    activity_type = models.CharField(
        max_length=50,
        choices=ActivityType.choices,
        default=ActivityType.OTHER,
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    occurred_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_activities",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-occurred_at", "-created_at"]
        indexes = [
            models.Index(fields=["activity_id"]),
            models.Index(fields=["contact"]),
            models.Index(fields=["company"]),
            models.Index(fields=["project"]),
            models.Index(fields=["activity_type"]),
            models.Index(fields=["occurred_at"]),
            models.Index(fields=["created_by"]),
            models.Index(fields=["deleted_at"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        if self.activity_id:
            return f"{self.activity_id} - {self.title}"
        return self.title

    def clean(self):
        if not self.company_id:
            raise ValidationError("An activity must be linked to a company.")
        if not self.title:
            raise ValidationError("An activity must have a title.")
        if self.contact_id and self.company_id:
            contact_company_id = getattr(self.contact, "company_id", None)
            if contact_company_id and contact_company_id != self.company_id:
                raise ValidationError(
                    "The selected contact does not belong to the selected company."
                )
        if self.project_id and self.company_id:
            project_company_id = getattr(self.project, "company_id", None)
            if project_company_id and project_company_id != self.company_id:
                raise ValidationError(
                    "The selected project does not belong to the selected company."
                )
