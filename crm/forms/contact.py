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
            "birthday",
            "preferred_language",
            "status",
            "notes",
        )
        widgets = {
            "birthday": forms.DateInput(attrs={"type": "date"}),
        }


class ContactEmailAddressForm(forms.ModelForm):
    class Meta:
        model = ContactEmailAddress
        fields = ("contact", "email", "type", "is_primary")


class ContactPhoneNumberForm(forms.ModelForm):
    class Meta:
        model = ContactPhoneNumber
        fields = ("contact", "phone_number", "type", "label", "is_primary")
