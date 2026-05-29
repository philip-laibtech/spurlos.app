from django.utils import timezone

from activities.models import Activity


def generate_activity_id() -> str:
    # TODO: replace with a high-concurrency-safe sequence if needed
    year = timezone.now().year
    prefix = f"ACT-{year}-"
    latest = (
        Activity.objects.filter(activity_id__startswith=prefix)
        .order_by("-activity_id")
        .values_list("activity_id", flat=True)
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
    return f"{prefix}{next_number:04d}"


def create_activity(
    company,
    title: str,
    contact=None,
    project=None,
    activity_type: str = "",
    description: str = "",
    occurred_at=None,
    created_by=None,
    activity_id: str = "",
) -> Activity:
    if not activity_id:
        activity_id = generate_activity_id()
    if occurred_at is None:
        occurred_at = timezone.now()
    activity = Activity(
        activity_id=activity_id,
        company=company,
        contact=contact,
        project=project,
        activity_type=activity_type or Activity.ActivityType.OTHER,
        title=title,
        description=description,
        occurred_at=occurred_at,
        created_by=created_by,
    )
    activity.full_clean()
    activity.save()
    return activity


ALLOWED_UPDATE_FIELDS = {"contact", "company", "project", "activity_type", "title", "description", "occurred_at"}


def update_activity(activity: Activity, **data) -> Activity:
    for field, value in data.items():
        if field in ALLOWED_UPDATE_FIELDS:
            setattr(activity, field, value)
    activity.full_clean()
    activity.save()
    return activity


def archive_activity(activity: Activity) -> Activity:
    activity.deleted_at = timezone.now()
    activity.save(update_fields=["deleted_at", "updated_at"])
    return activity


def restore_activity(activity: Activity) -> Activity:
    activity.deleted_at = None
    activity.save(update_fields=["deleted_at", "updated_at"])
    return activity
