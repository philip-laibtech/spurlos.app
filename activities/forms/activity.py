from django import forms

from activities.models import Activity
from projects.models import Project


class ProjectByCompanyWidget(forms.Select):
    """Select widget that adds data-company-id to each project <option>."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._company_map: dict[str, str] = {}

    def set_company_map(self, queryset) -> None:
        self._company_map = {str(p.pk): str(p.company_id) for p in queryset}

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        if value:
            company_id = self._company_map.get(str(value))
            if company_id:
                option["attrs"]["data-company-id"] = company_id
        return option


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = (
            "company",
            "contact",
            "project",
            "activity_type",
            "title",
            "description",
            "occurred_at",
        )
        widgets = {
            "occurred_at": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
            "description": forms.Textarea(attrs={"rows": 4}),
            "project": ProjectByCompanyWidget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        project_qs = Project.objects.filter(deleted_at__isnull=True).select_related("company").order_by("company__name", "title")
        self.fields["project"].queryset = project_qs
        self.fields["project"].widget.set_company_map(project_qs)

        if self.instance and self.instance.pk and self.instance.occurred_at:
            self.fields["occurred_at"].initial = self.instance.occurred_at.strftime("%Y-%m-%dT%H:%M")

    def clean(self):
        cleaned_data = super().clean()
        company = cleaned_data.get("company")
        contact = cleaned_data.get("contact")
        project = cleaned_data.get("project")

        if contact and company and contact.company_id:
            if contact.company_id != company.pk:
                self.add_error("contact", "The selected contact does not belong to the selected company.")

        if project and company:
            if project.company_id != company.pk:
                self.add_error("project", "The selected project does not belong to the selected company.")

        return cleaned_data
