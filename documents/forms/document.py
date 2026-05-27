from django import forms

from documents.models import Document
from documents.services.documents import ALLOWED_DOCUMENT_EXTENSIONS, MAX_DOCUMENT_FILE_SIZE_BYTES


class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ("title", "description", "file", "company", "contact", "project", "task")

    def clean_file(self):
        uploaded_file = self.cleaned_data.get("file")
        if not uploaded_file:
            raise forms.ValidationError("A file is required.")
        if uploaded_file.size > MAX_DOCUMENT_FILE_SIZE_BYTES:
            max_mb = MAX_DOCUMENT_FILE_SIZE_BYTES // (1024 * 1024)
            raise forms.ValidationError(f"File size must not exceed {max_mb} MB.")
        ext = uploaded_file.name.rsplit(".", 1)[-1].lower() if "." in uploaded_file.name else ""
        if ext not in ALLOWED_DOCUMENT_EXTENSIONS:
            raise forms.ValidationError(
                f"File type '.{ext}' is not allowed. "
                f"Allowed types: {', '.join(sorted(ALLOWED_DOCUMENT_EXTENSIONS))}."
            )
        return uploaded_file

    def clean(self):
        cleaned_data = super().clean()
        company = cleaned_data.get("company")
        contact = cleaned_data.get("contact")
        project = cleaned_data.get("project")
        task = cleaned_data.get("task")

        if not any([company, contact, project, task]):
            raise forms.ValidationError(
                "Please link the document to at least one of: company, contact, project, or task."
            )

        if task and project and task.project_id != project.pk:
            raise forms.ValidationError("The selected task does not belong to the selected project.")

        if project and company and project.company_id != company.pk:
            raise forms.ValidationError("The selected project does not belong to the selected company.")

        if contact and company and contact.company_id != company.pk:
            raise forms.ValidationError("The selected contact does not belong to the selected company.")

        return cleaned_data
