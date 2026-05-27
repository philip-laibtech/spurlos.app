from django.contrib import admin

from documents.models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        "document_id",
        "title",
        "original_filename",
        "company",
        "contact",
        "project",
        "task",
        "uploaded_by",
        "file_size",
        "mime_type",
        "created_at",
    )
    search_fields = (
        "document_id",
        "title",
        "description",
        "original_filename",
        "company__name",
        "company__legal_name",
        "contact__first_name",
        "contact__last_name",
        "project__title",
        "task__title",
        "uploaded_by__email",
    )
    list_filter = ("mime_type", "created_at", "updated_at", "deleted_at")
    autocomplete_fields = ("company", "contact", "project", "task", "uploaded_by")
    readonly_fields = (
        "document_id",
        "original_filename",
        "file_size",
        "mime_type",
        "created_at",
        "updated_at",
    )
