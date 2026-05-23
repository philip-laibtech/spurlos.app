from django.contrib import admin

from crm.models import Contact, ContactEmailAddress, ContactPhoneNumber


class ContactEmailAddressInline(admin.TabularInline):
    model = ContactEmailAddress
    extra = 0
    fields = ("email", "type", "is_primary")


class ContactPhoneNumberInline(admin.TabularInline):
    model = ContactPhoneNumber
    extra = 0
    fields = ("phone_number", "type", "label", "is_primary")


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "salutation", "company", "job_title", "status", "created_at")
    list_filter = ("status", "preferred_language", "salutation")
    search_fields = ("first_name", "last_name", "company__name", "job_title")
    readonly_fields = ("created_at", "updated_at")
    inlines = [ContactEmailAddressInline, ContactPhoneNumberInline]
    fieldsets = (
        (None, {
            "fields": ("salutation", "first_name", "last_name", "status"),
        }),
        ("Work", {
            "fields": ("company", "job_title", "department"),
        }),
        ("Personal", {
            "fields": ("birthday", "preferred_language", "notes"),
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at", "deleted_at"),
            "classes": ("collapse",),
        }),
    )


@admin.register(ContactEmailAddress)
class ContactEmailAddressAdmin(admin.ModelAdmin):
    list_display = ("email", "contact", "type", "is_primary")
    list_filter = ("type", "is_primary")
    search_fields = ("email", "contact__first_name", "contact__last_name")


@admin.register(ContactPhoneNumber)
class ContactPhoneNumberAdmin(admin.ModelAdmin):
    list_display = ("phone_number", "contact", "type", "label", "is_primary")
    list_filter = ("type", "is_primary")
    search_fields = ("phone_number", "contact__first_name", "contact__last_name")
