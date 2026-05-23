from django.contrib import admin

from crm.models import Address


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("line1", "postal_code", "city", "country")
    search_fields = ("line1", "postal_code", "city", "country")
