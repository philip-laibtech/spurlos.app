from django.db.models import Q, QuerySet

from projects.models import Project


def get_project_queryset() -> QuerySet:
    return Project.objects.filter(deleted_at__isnull=True).select_related("company", "contact")


def get_project_list() -> QuerySet:
    return get_project_queryset()


def get_project_detail(project_id: int) -> Project:
    return get_project_queryset().get(pk=project_id)


def get_projects_for_company(company) -> QuerySet:
    return get_project_queryset().filter(company=company)


def get_projects_for_contact(contact) -> QuerySet:
    return get_project_queryset().filter(contact=contact)


def search_projects(query: str) -> QuerySet:
    if not query:
        return get_project_queryset()
    return (
        get_project_queryset().filter(
            Q(title__icontains=query)
            | Q(company__name__icontains=query)
            | Q(contact__first_name__icontains=query)
            | Q(contact__last_name__icontains=query)
        ).distinct()
    )
