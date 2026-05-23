from django.db.models import QuerySet

from crm.models import Company, Contact


def get_contact_queryset() -> QuerySet:
    return Contact.objects.filter(deleted_at__isnull=True)


def get_contact_list() -> QuerySet:
    return (
        get_contact_queryset()
        .select_related("company")
        .prefetch_related("email_addresses", "phone_numbers")
        .order_by("last_name", "first_name")
    )


def get_contact_detail(contact_id: int) -> Contact:
    return (
        get_contact_queryset()
        .select_related("company")
        .prefetch_related("email_addresses", "phone_numbers")
        .get(pk=contact_id)
    )


def get_contacts_for_company(company: Company) -> QuerySet:
    return (
        get_contact_queryset()
        .filter(company=company)
        .prefetch_related("email_addresses", "phone_numbers")
        .order_by("last_name", "first_name")
    )


def search_contacts(query: str) -> QuerySet:
    return (
        get_contact_queryset().filter(first_name__icontains=query)
        | get_contact_queryset().filter(last_name__icontains=query)
        | get_contact_queryset().filter(company__name__icontains=query)
    ).distinct().select_related("company").order_by("last_name", "first_name")
