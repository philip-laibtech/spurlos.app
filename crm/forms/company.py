from django import forms

from crm.models import Address, Company, CompanyLocation, CompanyPhoneNumber


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = (
            "name",
            "legal_name",
            "company_type",
            "status",
            "domain",
            "website",
            "main_email",
            "uid_number",
            "vat_number",
            "industry",
            "notes",
        )


class CompanyLocationForm(forms.ModelForm):
    class Meta:
        model = CompanyLocation
        fields = ("company", "address", "name", "type")


class CompanyLocationAddForm(forms.Form):
    """Used when adding a location from a company's detail page. Creates Address inline."""

    # Location fields
    name = forms.CharField(max_length=255, label="Location name")
    type = forms.ChoiceField(choices=CompanyLocation.LocationType.choices, label="Type")
    # Address fields
    line1 = forms.CharField(max_length=255, label="Street")
    line2 = forms.CharField(max_length=255, required=False, label="Street line 2")
    postal_code = forms.CharField(max_length=30, label="Postal code")
    city = forms.CharField(max_length=120, label="City")
    state_region = forms.CharField(max_length=120, required=False, label="State / Region")
    country = forms.CharField(max_length=120, initial="Switzerland", label="Country")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.data and not self.initial.get("country"):
            self.fields["country"].initial = "Switzerland"


class CompanyPhoneNumberForm(forms.ModelForm):
    class Meta:
        model = CompanyPhoneNumber
        fields = ("company", "location", "phone_number", "type", "label", "is_primary")


class CompanyPhoneNumberAddForm(forms.ModelForm):
    """Used when adding a phone number directly from a company's detail page."""

    class Meta:
        model = CompanyPhoneNumber
        fields = ("phone_number", "type", "label", "is_primary")
