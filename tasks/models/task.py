from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Task(models.Model):
    task_id = models.CharField(max_length=50, unique=True, blank=True, db_index=True)
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.PROTECT,
        related_name="tasks",
    )
    assigned_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["due_date", "-created_at"]
        indexes = [
            models.Index(fields=["task_id"]),
            models.Index(fields=["project"]),
            models.Index(fields=["assigned_user"]),
            models.Index(fields=["due_date"]),
            models.Index(fields=["deleted_at"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        if self.task_id:
            return f"{self.task_id} - {self.title}"
        return self.title

    def clean(self):
        if not self.project_id:
            raise ValidationError("A task must be assigned to a project.")
        if not self.title:
            raise ValidationError("A task must have a title.")
