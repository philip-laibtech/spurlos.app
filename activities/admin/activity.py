from django.contrib import admin

from activities.models import Activity


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = (
        "activity_id",
        "activity_type",
        "title",
        "contact",
        "company",
        "project",
        "occurred_at",
        "created_by",
        "created_at",
    )
    search_fields = (
        "activity_id",
        "title",
        "description",
        "contact__first_name",
        "contact__last_name",
        "contact__email_addresses__email",
        "company__name",
        "company__legal_name",
        "project__title",
        "created_by__email",
    )
    list_filter = ("activity_type", "occurred_at", "created_at", "updated_at", "deleted_at")
    autocomplete_fields = ("contact", "company", "project", "created_by")
    readonly_fields = ("activity_id", "created_at", "updated_at")
