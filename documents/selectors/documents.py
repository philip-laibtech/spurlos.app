from django.db.models import Q, QuerySet

from documents.models import Document


def get_document_queryset() -> QuerySet:
    return Document.objects.filter(deleted_at__isnull=True).select_related(
        "company", "contact", "project", "task", "uploaded_by"
    )


def get_document_list() -> QuerySet:
    return get_document_queryset()


def get_document_detail(document_pk: int) -> Document:
    return get_document_queryset().get(pk=document_pk)


def get_document_by_document_id(document_id: str) -> Document:
    return get_document_queryset().get(document_id=document_id)


def get_documents_for_company(company) -> QuerySet:
    return get_document_queryset().filter(company=company)


def get_documents_for_contact(contact) -> QuerySet:
    return get_document_queryset().filter(contact=contact)


def get_documents_for_project(project) -> QuerySet:
    return get_document_queryset().filter(project=project)


def get_documents_for_task(task) -> QuerySet:
    return get_document_queryset().filter(task=task)


def search_documents(query: str) -> QuerySet:
    if not query:
        return get_document_queryset()
    return (
        get_document_queryset()
        .filter(
            Q(document_id__icontains=query)
            | Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(original_filename__icontains=query)
            | Q(company__name__icontains=query)
            | Q(contact__first_name__icontains=query)
            | Q(contact__last_name__icontains=query)
            | Q(project__title__icontains=query)
            | Q(task__title__icontains=query)
        )
        .distinct()
    )
