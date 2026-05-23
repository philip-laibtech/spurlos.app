from django.db.models import QuerySet

from crm.models import Company


def get_company_queryset() -> QuerySet:
    return Company.objects.filter(deleted_at__isnull=True)


def get_company_list() -> QuerySet:
    return (
        get_company_queryset()
        .select_related("hq_location__address")
        .prefetch_related("locations", "phone_numbers", "contacts")
        .order_by("name")
    )


def get_company_detail(company_id: int) -> Company:
    return (
        get_company_queryset()
        .select_related("hq_location__address")
        .prefetch_related(
            "locations__address",
            "phone_numbers",
            "contacts",
        )
        .get(pk=company_id)
    )


def get_companies_by_status(status: str) -> QuerySet:
    return get_company_queryset().filter(status=status).order_by("name")


def search_companies(query: str) -> QuerySet:
    return (
        get_company_queryset().filter(name__icontains=query)
        | get_company_queryset().filter(legal_name__icontains=query)
    ).distinct().order_by("name")
