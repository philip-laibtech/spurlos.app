from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from projects.models import Project

User = get_user_model()


class UserChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        full_name = f"{obj.first_name} {obj.last_name}".strip()
        return full_name or obj.email


class ProjectForm(forms.ModelForm):
    assigned_to = UserChoiceField(
        queryset=User.objects.filter(is_active=True).order_by("first_name", "last_name", "email"),
        required=False,
        empty_label="— Unassigned",
    )

    class Meta:
        model = Project
        fields = ("title", "company", "contact", "assigned_to", "description")

    def clean(self):
        cleaned_data = super().clean()
        company = cleaned_data.get("company")
        contact = cleaned_data.get("contact")
        if contact and company and contact.company_id != company.pk:
            raise ValidationError(
                "The selected contact does not belong to the selected company."
            )
        return cleaned_data
