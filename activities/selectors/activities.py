from django.db.models import Q, QuerySet

from activities.models import Activity


def get_activity_queryset() -> QuerySet:
    return Activity.objects.filter(deleted_at__isnull=True).select_related(
        "contact", "company", "project", "created_by"
    )


def get_activity_list() -> QuerySet:
    return get_activity_queryset()


def get_activity_detail(activity_pk: int) -> Activity:
    return get_activity_queryset().get(pk=activity_pk)


def get_activity_by_activity_id(activity_id: str) -> Activity:
    return get_activity_queryset().get(activity_id=activity_id)


def get_activities_for_contact(contact) -> QuerySet:
    return get_activity_queryset().filter(contact=contact)


def get_activities_for_company(company) -> QuerySet:
    return get_activity_queryset().filter(company=company)


def get_activities_for_project(project) -> QuerySet:
    return get_activity_queryset().filter(project=project)


def get_activities_by_type(activity_type: str) -> QuerySet:
    return get_activity_queryset().filter(activity_type=activity_type)


def search_activities(query: str) -> QuerySet:
    if not query:
        return get_activity_queryset()
    return (
        get_activity_queryset()
        .filter(
            Q(activity_id__icontains=query)
            | Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(contact__first_name__icontains=query)
            | Q(contact__last_name__icontains=query)
            | Q(contact__email_addresses__email__icontains=query)
            | Q(company__name__icontains=query)
            | Q(project__title__icontains=query)
        )
        .distinct()
    )
