from django.utils import timezone

from projects.models import Project


ALLOWED_UPDATE_FIELDS = {"title", "company", "contact", "assigned_to", "description", "status"}


def generate_project_number() -> str:
    # TODO: replace with a high-concurrency-safe sequence if needed
    year = timezone.now().year
    prefix = f"SL{year}"
    latest = (
        Project.objects.filter(project_number__startswith=prefix)
        .order_by("-project_number")
        .values_list("project_number", flat=True)
        .first()
    )
    if latest:
        try:
            last_number = int(latest[len(prefix):])
        except (ValueError, IndexError):
            last_number = 0
        next_number = last_number + 1
    else:
        next_number = 1
    return f"{prefix}{next_number:05d}"


def create_project(
    company,
    title: str,
    contact=None,
    assigned_to=None,
    description: str = "",
    status: str = "",
    project_number: str = "",
) -> Project:
    if not project_number:
        project_number = generate_project_number()
    project = Project(
        company=company,
        title=title,
        contact=contact,
        assigned_to=assigned_to,
        description=description,
        status=status or Project.Status.PLANNED,
        project_number=project_number,
    )
    project.full_clean()
    project.save()
    return project


def update_project(project: Project, **data) -> Project:
    for field, value in data.items():
        if field in ALLOWED_UPDATE_FIELDS:
            setattr(project, field, value)
    project.full_clean()
    project.save()
    return project


def archive_project(project: Project) -> Project:
    project.deleted_at = timezone.now()
    project.save(update_fields=["deleted_at", "updated_at"])
    return project


def restore_project(project: Project) -> Project:
    project.deleted_at = None
    project.save(update_fields=["deleted_at", "updated_at"])
    return project
