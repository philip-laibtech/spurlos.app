from django import forms

from crm.models import Contact, ContactEmailAddress, ContactPhoneNumber


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = (
            "company",
            "salutation",
            "first_name",
            "last_name",
            "job_title",
            "department",
            "work_location",
            "linkedin_url",
            "birthday",
            "preferred_language",
            "status",
            "notes",
        )
        widgets = {
            "birthday": forms.DateInput(attrs={"type": "date"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        company = cleaned_data.get("company")
        work_location = cleaned_data.get("work_location")
        if work_location and company and work_location.company_id != company.pk:
            raise forms.ValidationError(
                "The selected work location does not belong to the selected company."
            )
        return cleaned_data


class ContactEmailAddressForm(forms.ModelForm):
    class Meta:
        model = ContactEmailAddress
        fields = ("contact", "email", "type", "is_primary")


class ContactPhoneNumberForm(forms.ModelForm):
    class Meta:
        model = ContactPhoneNumber
        fields = ("contact", "phone_number", "type", "label", "is_primary")
