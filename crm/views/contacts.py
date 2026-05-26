from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View

from crm.forms import ContactForm
from crm.models import Contact
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
