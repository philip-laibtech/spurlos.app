from django.urls import path

from documents.views.documents import (
    DocumentDeleteView,
    DocumentDetailView,
    DocumentDownloadView,
    DocumentListView,
    DocumentUploadView,
)

app_name = "documents"

urlpatterns = [
    path("", DocumentListView.as_view(), name="document_list"),
    path("upload/", DocumentUploadView.as_view(), name="document_upload"),
    path("<int:pk>/", DocumentDetailView.as_view(), name="document_detail"),
    path("<int:pk>/download/", DocumentDownloadView.as_view(), name="document_download"),
    path("<int:pk>/delete/", DocumentDeleteView.as_view(), name="document_delete"),
]
