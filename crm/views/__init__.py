from .companies import (
    CompanyCreateView,
    CompanyDeleteView,
    CompanyDetailView,
    CompanyListView,
    CompanyLocationCreateView,
    CompanyLocationDeleteView,
    CompanyLocationUpdateView,
    CompanyPhoneNumberCreateView,
    CompanyPhoneNumberDeleteView,
    CompanyPhoneNumberUpdateView,
    CompanyUpdateView,
)
from .contacts import (
    ContactCreateView,
    ContactDeleteView,
    ContactDetailView,
    ContactListView,
    ContactUpdateView,
)

__all__ = [
    "CompanyListView",
    "CompanyDetailView",
    "CompanyCreateView",
    "CompanyUpdateView",
    "CompanyDeleteView",
    "CompanyLocationCreateView",
    "CompanyLocationUpdateView",
    "CompanyLocationDeleteView",
    "CompanyPhoneNumberCreateView",
    "CompanyPhoneNumberUpdateView",
    "CompanyPhoneNumberDeleteView",
    "ContactListView",
    "ContactDetailView",
    "ContactCreateView",
    "ContactUpdateView",
    "ContactDeleteView",
]
