import mimetypes
import os

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import DetailView, ListView, View

from documents.forms import DocumentUploadForm
from documents.models import Document
from documents.selectors import get_document_detail, get_document_list, search_documents
from documents.services import archive_document, create_document


class DocumentListView(LoginRequiredMixin, ListView):
    template_name = "documents/list.html"
    context_object_name = "documents"

    def get_queryset(self):
        q = self.request.GET.get("q", "").strip()
        if q:
            return search_documents(q)
        return get_document_list()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["query"] = self.request.GET.get("q", "")
        return ctx


class DocumentDetailView(LoginRequiredMixin, DetailView):
    template_name = "documents/detail.html"
    context_object_name = "document"

    def get_object(self):
        return get_document_detail(self.kwargs["pk"])


class DocumentUploadView(LoginRequiredMixin, View):
    template_name = "documents/upload_form.html"

    def get(self, request):
        initial = {}
        for key in ("company", "contact", "project", "task"):
            val = request.GET.get(key)
            if val:
                initial[key] = val
        form = DocumentUploadForm(initial=initial)
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            d = form.cleaned_data
            doc = create_document(
                file=d["file"],
                title=d.get("title", ""),
                description=d.get("description", ""),
                company=d.get("company"),
                contact=d.get("contact"),
                project=d.get("project"),
                task=d.get("task"),
                uploaded_by=request.user if request.user.is_authenticated else None,
            )
            return redirect(reverse("documents:document_detail", kwargs={"pk": doc.pk}))
        return render(request, self.template_name, {"form": form})


class DocumentDeleteView(LoginRequiredMixin, View):
    template_name = "documents/confirm_delete.html"

    def _get_document(self, pk):
        return get_object_or_404(Document, pk=pk, deleted_at__isnull=True)

    def get(self, request, pk):
        document = self._get_document(pk)
        return render(request, self.template_name, {"document": document})

    def post(self, request, pk):
        document = self._get_document(pk)
        archive_document(document)
        return redirect(reverse("documents:document_list"))


class DocumentDownloadView(LoginRequiredMixin, View):
    def get(self, request, pk):
        document = get_object_or_404(Document, pk=pk, deleted_at__isnull=True)
        if not document.file:
            raise Http404("File not found.")

        storage = document.file.storage
        if not storage.exists(document.file.name):
            raise Http404("File not found.")

        file_handle = storage.open(document.file.name, "rb")
        content_type = document.mime_type or "application/octet-stream"
        if not document.mime_type:
            guessed, _ = mimetypes.guess_type(document.original_filename or document.file.name)
            if guessed:
                content_type = guessed

        filename = document.original_filename or os.path.basename(document.file.name)
        response = FileResponse(file_handle, content_type=content_type)
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
