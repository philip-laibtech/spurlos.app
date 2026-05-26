from django.utils import timezone

from projects.models import Project


ALLOWED_UPDATE_FIELDS = {"title", "company", "contact"}


def create_project(company, title: str, contact=None) -> Project:
    project = Project(company=company, title=title, contact=contact)
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
