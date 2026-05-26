from django.contrib import admin

from projects.models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("project_number", "title", "company", "contact", "assigned_to", "created_at", "updated_at")
    readonly_fields = ("project_number", "created_at", "updated_at")
    search_fields = (
        "title",
        "company__name",
        "company__legal_name",
        "contact__first_name",
        "contact__last_name",
        "contact__email_addresses__email",
    )
    list_filter = ("created_at", "updated_at", "deleted_at")
    autocomplete_fields = ("company", "contact")
