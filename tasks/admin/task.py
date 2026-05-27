from django.contrib import admin

from tasks.models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("task_id", "title", "project", "assigned_user", "due_date", "created_at", "updated_at")
    search_fields = (
        "task_id",
        "title",
        "description",
        "project__title",
        "project__company__name",
        "assigned_user__email",
        "assigned_user__first_name",
        "assigned_user__last_name",
    )
    list_filter = ("due_date", "created_at", "updated_at", "deleted_at")
    autocomplete_fields = ("project", "assigned_user")
    readonly_fields = ("created_at", "updated_at")
