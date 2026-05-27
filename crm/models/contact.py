from django.core.exceptions import ValidationError
from django.db import models


class Contact(models.Model):
    class Salutation(models.TextChoices):
        HERR = "herr", "Mr."
        FRAU = "frau", "Mrs."
        DIVERS = "divers", "Unknown"

    class Language(models.TextChoices):
        DE = "de", "German"
        EN = "en", "English"
        FR = "fr", "French"
        IT = "it", "Italian"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        LEFT_COMPANY = "left_company", "Left Company"
        ARCHIVED = "archived", "Archived"
        DO_NOT_CONTACT = "do_not_contact", "Do Not Contact"

    company = models.ForeignKey(
        "crm.Company",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contacts",
    )
    salutation = models.CharField(
        max_length=10,
        choices=Salutation.choices,
        blank=True,
    )
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    job_title = models.CharField(max_length=150, blank=True)
    department = models.CharField(max_length=120, blank=True)
    birthday = models.DateField(null=True, blank=True)
    preferred_language = models.CharField(
        max_length=10,
        choices=Language.choices,
        blank=True,
    )
    status = models.CharField(
        max_length=50,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    work_location = models.ForeignKey(
        "crm.CompanyLocation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contacts",
    )
    linkedin_url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["last_name", "first_name"]),
            models.Index(fields=["company"]),
            models.Index(fields=["status"]),
            models.Index(fields=["work_location"]),
        ]

    def clean(self):
        if self.work_location_id and self.company_id:
            if self.work_location.company_id != self.company_id:
                raise ValidationError(
                    "The selected work location does not belong to the selected company."
                )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class ContactEmailAddress(models.Model):
    class EmailType(models.TextChoices):
        WORK = "work", "Work"
        PRIVATE = "private", "Private"
        OTHER = "other", "Other"

    contact = models.ForeignKey(
        "crm.Contact",
        on_delete=models.CASCADE,
        related_name="email_addresses",
    )
    email = models.EmailField()
    type = models.CharField(
        max_length=50,
        choices=EmailType.choices,
        default=EmailType.WORK,
    )
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["contact"]),
            models.Index(fields=["is_primary"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["contact"],
                condition=models.Q(is_primary=True),
                name="unique_contact_primary_email",
            )
        ]

    def __str__(self):
        return self.email


class ContactPhoneNumber(models.Model):
    class PhoneType(models.TextChoices):
        MOBILE = "mobile", "Mobile"
        WORK = "work", "Work"
        PRIVATE = "private", "Private"
        OTHER = "other", "Other"

    contact = models.ForeignKey(
        "crm.Contact",
        on_delete=models.CASCADE,
        related_name="phone_numbers",
    )
    phone_number = models.CharField(max_length=50)
    type = models.CharField(
        max_length=50,
        choices=PhoneType.choices,
        default=PhoneType.MOBILE,
    )
    label = models.CharField(max_length=100, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["contact"]),
            models.Index(fields=["phone_number"]),
            models.Index(fields=["is_primary"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["contact"],
                condition=models.Q(is_primary=True),
                name="unique_contact_primary_phone",
            )
        ]

    def __str__(self):
        return self.phone_number
