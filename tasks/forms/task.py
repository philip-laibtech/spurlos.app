from django import forms
from django.contrib.auth import get_user_model

from tasks.models import Task

User = get_user_model()


class UserChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        full_name = f"{obj.first_name} {obj.last_name}".strip()
        return full_name or obj.email


class TaskForm(forms.ModelForm):
    assigned_user = UserChoiceField(
        queryset=User.objects.filter(is_active=True).order_by("first_name", "last_name", "email"),
        required=False,
        empty_label="— Unassigned",
    )

    class Meta:
        model = Task
        fields = ("project", "assigned_user", "title", "description", "due_date")
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["project"].disabled = True
