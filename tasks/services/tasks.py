from django.utils import timezone

from tasks.models import Task


def generate_task_id(project) -> str:
    # TODO: replace with a high-concurrency-safe sequence if needed (e.g. database sequence or Redis counter)
    year = timezone.now().year
    prefix = f"TASK{year}{project.pk:05d}-"
    latest = (
        Task.objects.filter(task_id__startswith=prefix)
        .order_by("-task_id")
        .values_list("task_id", flat=True)
        .first()
    )
    if latest:
        try:
            last_number = int(latest.split("-")[-1])
        except (ValueError, IndexError):
            last_number = 0
        next_number = last_number + 1
    else:
        next_number = 1
    return f"{prefix}{next_number:02d}"


def create_task(
    project,
    title: str,
    assigned_user=None,
    description: str = "",
    due_date=None,
    task_id: str = "",
) -> Task:
    if not task_id:
        task_id = generate_task_id(project)
    task = Task(
        task_id=task_id,
        project=project,
        title=title,
        assigned_user=assigned_user,
        description=description,
        due_date=due_date,
    )
    task.full_clean()
    task.save()
    return task


ALLOWED_UPDATE_FIELDS = {"assigned_user", "title", "description", "due_date"}


def update_task(task: Task, **data) -> Task:
    for field, value in data.items():
        if field in ALLOWED_UPDATE_FIELDS:
            setattr(task, field, value)
    task.full_clean()
    task.save()
    return task


def archive_task(task: Task) -> Task:
    task.deleted_at = timezone.now()
    task.save(update_fields=["deleted_at", "updated_at"])
    return task


def restore_task(task: Task) -> Task:
    task.deleted_at = None
    task.save(update_fields=["deleted_at", "updated_at"])
    return task
