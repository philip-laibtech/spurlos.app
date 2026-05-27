from django.db.models import Q, QuerySet

from tasks.models import Task


def get_task_queryset() -> QuerySet:
    return Task.objects.filter(deleted_at__isnull=True).select_related(
        "project", "project__company", "assigned_user"
    )


def get_task_list() -> QuerySet:
    return get_task_queryset()


def get_task_detail(task_pk: int) -> Task:
    return get_task_queryset().get(pk=task_pk)


def get_task_by_task_id(task_id: str) -> Task:
    return get_task_queryset().get(task_id=task_id)


def get_tasks_for_project(project) -> QuerySet:
    return get_task_queryset().filter(project=project)


def get_tasks_for_user(user) -> QuerySet:
    return get_task_queryset().filter(assigned_user=user)


def search_tasks(query: str) -> QuerySet:
    if not query:
        return get_task_queryset()
    return (
        get_task_queryset()
        .filter(
            Q(task_id__icontains=query)
            | Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(project__title__icontains=query)
            | Q(project__company__name__icontains=query)
            | Q(assigned_user__email__icontains=query)
            | Q(assigned_user__first_name__icontains=query)
            | Q(assigned_user__last_name__icontains=query)
        )
        .distinct()
    )
