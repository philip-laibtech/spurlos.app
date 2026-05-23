from django.urls import path

from crm.views import (
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
    ContactCreateView,
    ContactDeleteView,
    ContactDetailView,
    ContactListView,
    ContactUpdateView,
)

app_name = "crm"

urlpatterns = [
    # Companies
    path("companies/", CompanyListView.as_view(), name="company_list"),
    path("companies/create/", CompanyCreateView.as_view(), name="company_create"),
    path("companies/<int:pk>/", CompanyDetailView.as_view(), name="company_detail"),
    path("companies/<int:pk>/edit/", CompanyUpdateView.as_view(), name="company_update"),
    path("companies/<int:pk>/delete/", CompanyDeleteView.as_view(), name="company_delete"),

    # Company locations
    path("companies/<int:company_pk>/add-location/", CompanyLocationCreateView.as_view(), name="company_location_create"),
    path("companies/<int:company_pk>/locations/<int:pk>/edit/", CompanyLocationUpdateView.as_view(), name="company_location_update"),
    path("companies/<int:company_pk>/locations/<int:pk>/delete/", CompanyLocationDeleteView.as_view(), name="company_location_delete"),

    # Company phone numbers
    path("companies/<int:company_pk>/add-phone/", CompanyPhoneNumberCreateView.as_view(), name="company_phone_create"),
    path("companies/<int:company_pk>/phones/<int:pk>/edit/", CompanyPhoneNumberUpdateView.as_view(), name="company_phone_update"),
    path("companies/<int:company_pk>/phones/<int:pk>/delete/", CompanyPhoneNumberDeleteView.as_view(), name="company_phone_delete"),

    # Contacts
    path("contacts/", ContactListView.as_view(), name="contact_list"),
    path("contacts/create/", ContactCreateView.as_view(), name="contact_create"),
    path("contacts/<int:pk>/", ContactDetailView.as_view(), name="contact_detail"),
    path("contacts/<int:pk>/edit/", ContactUpdateView.as_view(), name="contact_update"),
    path("contacts/<int:pk>/delete/", ContactDeleteView.as_view(), name="contact_delete"),
]
