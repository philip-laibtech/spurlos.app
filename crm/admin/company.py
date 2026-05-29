from django.contrib import admin

from crm.models import Company, CompanyLocation, CompanyPhoneNumber


class CompanyLocationInline(admin.TabularInline):
    model = CompanyLocation
    extra = 0
    fields = ("name", "type", "address")
    autocomplete_fields = ("address",)


class CompanyPhoneNumberInline(admin.TabularInline):
    model = CompanyPhoneNumber
    extra = 0
    fields = ("phone_number", "type", "label", "location", "is_primary")


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "company_type", "status", "industry", "created_at")
    list_filter = ("company_type", "status", "industry")
    search_fields = ("name", "legal_name", "main_email")
    readonly_fields = ("created_at", "updated_at")
    inlines = [CompanyLocationInline, CompanyPhoneNumberInline]
    fieldsets = (
        (None, {
            "fields": ("name", "legal_name", "company_type", "status"),
        }),
        ("Contact & Web", {
            "fields": ("website", "main_email"),
        }),
        ("Details", {
            "fields": ("industry", "notes"),
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at", "deleted_at"),
            "classes": ("collapse",),
        }),
    )


@admin.register(CompanyLocation)
class CompanyLocationAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "type")
    list_filter = ("type",)
    search_fields = ("name", "company__name")
    autocomplete_fields = ("address",)


@admin.register(CompanyPhoneNumber)
class CompanyPhoneNumberAdmin(admin.ModelAdmin):
    list_display = ("phone_number", "company", "type", "label", "is_primary")
    list_filter = ("type", "is_primary")
    search_fields = ("phone_number", "company__name", "label")
