from django.core.exceptions import ValidationError

from crm.models import Company, CompanyLocation, Contact, ContactEmailAddress, ContactPhoneNumber


def create_contact(first_name: str, last_name: str, **data) -> Contact:
    contact = Contact(first_name=first_name, last_name=last_name, **data)
    contact.full_clean()
    contact.save()
    return contact


def update_contact(contact: Contact, **data) -> Contact:
    for field, value in data.items():
        setattr(contact, field, value)
    contact.full_clean()
    contact.save()
    return contact


def add_contact_email(contact: Contact, email: str, **data) -> ContactEmailAddress:
    email_address = ContactEmailAddress(contact=contact, email=email, **data)
    email_address.full_clean()
    email_address.save()
    return email_address


def add_contact_phone_number(contact: Contact, phone_number: str, **data) -> ContactPhoneNumber:
    phone = ContactPhoneNumber(contact=contact, phone_number=phone_number, **data)
    phone.full_clean()
    phone.save()
    return phone


def set_primary_contact_email(contact: Contact, email_address: ContactEmailAddress) -> ContactEmailAddress:
    if email_address.contact_id != contact.pk:
        raise ValidationError("Email address does not belong to this contact.")
    ContactEmailAddress.objects.filter(contact=contact, is_primary=True).exclude(pk=email_address.pk).update(
        is_primary=False
    )
    email_address.is_primary = True
    email_address.save(update_fields=["is_primary", "updated_at"])
    return email_address


def set_primary_contact_phone(contact: Contact, phone_number: ContactPhoneNumber) -> ContactPhoneNumber:
    if phone_number.contact_id != contact.pk:
        raise ValidationError("Phone number does not belong to this contact.")
    ContactPhoneNumber.objects.filter(contact=contact, is_primary=True).exclude(pk=phone_number.pk).update(
        is_primary=False
    )
    phone_number.is_primary = True
    phone_number.save(update_fields=["is_primary", "updated_at"])
    return phone_number
