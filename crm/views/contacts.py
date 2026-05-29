from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View

from crm.forms import ContactEmailAddressAddForm, ContactForm, ContactPhoneNumberAddForm
from crm.models import Contact, ContactEmailAddress, ContactPhoneNumber
from activities.selectors import get_activities_for_contact
from crm.selectors import get_contact_detail, get_contact_list
from projects.selectors import get_projects_for_contact


class ContactListView(LoginRequiredMixin, ListView):
    template_name = "crm/contacts/list.html"
    context_object_name = "contacts"

    def get_queryset(self):
        return get_contact_list()


class ContactDetailView(LoginRequiredMixin, DetailView):
    template_name = "crm/contacts/detail.html"
    context_object_name = "contact"

    def get_object(self):
        return get_contact_detail(self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["contact_projects"] = get_projects_for_contact(self.object)
        ctx["contact_activities"] = get_activities_for_contact(self.object)
        return ctx


class ContactCreateView(LoginRequiredMixin, CreateView):
    template_name = "crm/contacts/form.html"
    form_class = ContactForm

    def get_initial(self):
        initial = super().get_initial()
        company_pk = self.request.GET.get("company")
        if company_pk:
            initial["company"] = company_pk
        return initial

    def get_success_url(self):
        company_pk = self.request.POST.get("company")
        if company_pk:
            return reverse_lazy("crm:company_detail", kwargs={"pk": company_pk})
        return reverse_lazy("crm:contact_list")


class ContactUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "crm/contacts/form.html"
    form_class = ContactForm
    context_object_name = "contact"

    def get_queryset(self):
        return Contact.objects.filter(deleted_at__isnull=True)

    def get_success_url(self):
        return reverse_lazy("crm:contact_detail", kwargs={"pk": self.object.pk})


class ContactDeleteView(LoginRequiredMixin, View):
    """Soft-deletes the contact by setting deleted_at."""

    def post(self, request, pk):
        contact = get_object_or_404(Contact, pk=pk, deleted_at__isnull=True)
        contact.deleted_at = timezone.now()
        contact.save(update_fields=["deleted_at", "updated_at"])
        return redirect("crm:contact_list")

    def get(self, request, pk):
        contact = get_object_or_404(Contact, pk=pk, deleted_at__isnull=True)
        return render(request, "crm/contacts/confirm_delete.html", {"contact": contact})


class ContactEmailCreateView(LoginRequiredMixin, View):
    def _get_contact(self, pk):
        return get_object_or_404(Contact, pk=pk, deleted_at__isnull=True)

    def get(self, request, contact_pk):
        contact = self._get_contact(contact_pk)
        form = ContactEmailAddressAddForm()
        return render(request, "crm/contacts/email_form.html", {
            "form": form, "contact": contact, "title": "Add Email Address",
        })

    def post(self, request, contact_pk):
        contact = self._get_contact(contact_pk)
        form = ContactEmailAddressAddForm(request.POST)
        if form.is_valid():
            email = form.save(commit=False)
            email.contact = contact
            email.save()
            return redirect(reverse("crm:contact_detail", kwargs={"pk": contact.pk}))
        return render(request, "crm/contacts/email_form.html", {
            "form": form, "contact": contact, "title": "Add Email Address",
        })


class ContactPhoneCreateView(LoginRequiredMixin, View):
    def _get_contact(self, pk):
        return get_object_or_404(Contact, pk=pk, deleted_at__isnull=True)

    def get(self, request, contact_pk):
        contact = self._get_contact(contact_pk)
        form = ContactPhoneNumberAddForm()
        return render(request, "crm/contacts/phone_form.html", {
            "form": form, "contact": contact, "title": "Add Phone Number",
        })

    def post(self, request, contact_pk):
        contact = self._get_contact(contact_pk)
        form = ContactPhoneNumberAddForm(request.POST)
        if form.is_valid():
            phone = form.save(commit=False)
            phone.contact = contact
            phone.save()
            return redirect(reverse("crm:contact_detail", kwargs={"pk": contact.pk}))
        return render(request, "crm/contacts/phone_form.html", {
            "form": form, "contact": contact, "title": "Add Phone Number",
        })


class ContactEmailUpdateView(LoginRequiredMixin, View):
    def _get_objects(self, contact_pk, pk):
        contact = get_object_or_404(Contact, pk=contact_pk, deleted_at__isnull=True)
        email = get_object_or_404(ContactEmailAddress, pk=pk, contact=contact)
        return contact, email

    def get(self, request, contact_pk, pk):
        contact, email = self._get_objects(contact_pk, pk)
        form = ContactEmailAddressAddForm(instance=email)
        return render(request, "crm/contacts/email_form.html", {
            "form": form, "contact": contact, "email": email, "title": f"Edit {email.email}",
        })

    def post(self, request, contact_pk, pk):
        contact, email = self._get_objects(contact_pk, pk)
        form = ContactEmailAddressAddForm(request.POST, instance=email)
        if form.is_valid():
            form.save()
            return redirect(reverse("crm:contact_detail", kwargs={"pk": contact.pk}))
        return render(request, "crm/contacts/email_form.html", {
            "form": form, "contact": contact, "email": email, "title": f"Edit {email.email}",
        })


class ContactEmailDeleteView(LoginRequiredMixin, View):
    def post(self, request, contact_pk, pk):
        contact = get_object_or_404(Contact, pk=contact_pk, deleted_at__isnull=True)
        email = get_object_or_404(ContactEmailAddress, pk=pk, contact=contact)
        email.delete()
        return redirect(reverse("crm:contact_detail", kwargs={"pk": contact.pk}))


class ContactPhoneUpdateView(LoginRequiredMixin, View):
    def _get_objects(self, contact_pk, pk):
        contact = get_object_or_404(Contact, pk=contact_pk, deleted_at__isnull=True)
        phone = get_object_or_404(ContactPhoneNumber, pk=pk, contact=contact)
        return contact, phone

    def get(self, request, contact_pk, pk):
        contact, phone = self._get_objects(contact_pk, pk)
        form = ContactPhoneNumberAddForm(instance=phone)
        return render(request, "crm/contacts/phone_form.html", {
            "form": form, "contact": contact, "phone": phone, "title": f"Edit {phone.phone_number}",
        })

    def post(self, request, contact_pk, pk):
        contact, phone = self._get_objects(contact_pk, pk)
        form = ContactPhoneNumberAddForm(request.POST, instance=phone)
        if form.is_valid():
            form.save()
            return redirect(reverse("crm:contact_detail", kwargs={"pk": contact.pk}))
        return render(request, "crm/contacts/phone_form.html", {
            "form": form, "contact": contact, "phone": phone, "title": f"Edit {phone.phone_number}",
        })


class ContactPhoneDeleteView(LoginRequiredMixin, View):
    def post(self, request, contact_pk, pk):
        contact = get_object_or_404(Contact, pk=contact_pk, deleted_at__isnull=True)
        phone = get_object_or_404(ContactPhoneNumber, pk=pk, contact=contact)
        phone.delete()
        return redirect(reverse("crm:contact_detail", kwargs={"pk": contact.pk}))
