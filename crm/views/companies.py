from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View

from crm.forms import CompanyForm, CompanyLocationAddForm, CompanyPhoneNumberAddForm
from crm.models import Address, Company, CompanyLocation, CompanyPhoneNumber
from activities.selectors import get_activities_for_company
from crm.selectors import get_company_detail, get_company_list
from projects.selectors import get_projects_for_company


class CompanyListView(LoginRequiredMixin, ListView):
    template_name = "crm/companies/list.html"
    context_object_name = "companies"

    def get_queryset(self):
        return get_company_list()


class CompanyDetailView(LoginRequiredMixin, DetailView):
    template_name = "crm/companies/detail.html"
    context_object_name = "company"

    def get_object(self):
        return get_company_detail(self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["company_projects"] = get_projects_for_company(self.object)
        ctx["company_activities"] = get_activities_for_company(self.object)
        return ctx


class CompanyCreateView(LoginRequiredMixin, CreateView):
    template_name = "crm/companies/form.html"
    form_class = CompanyForm

    def get_success_url(self):
        next_url = self.request.GET.get("next", "")
        if next_url.startswith("/"):
            return f"{next_url}?company={self.object.pk}"
        return reverse("crm:company_list")


class CompanyUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "crm/companies/form.html"
    form_class = CompanyForm
    context_object_name = "company"

    def get_queryset(self):
        return Company.objects.filter(deleted_at__isnull=True)

    def get_success_url(self):
        return reverse("crm:company_detail", kwargs={"pk": self.object.pk})


class CompanyDeleteView(LoginRequiredMixin, View):
    """Soft-deletes the company by setting deleted_at."""

    def post(self, request, pk):
        company = get_object_or_404(Company, pk=pk, deleted_at__isnull=True)
        company.deleted_at = timezone.now()
        company.save(update_fields=["deleted_at", "updated_at"])
        return redirect("crm:company_list")

    def get(self, request, pk):
        company = get_object_or_404(Company, pk=pk, deleted_at__isnull=True)
        return render(request, "crm/companies/confirm_delete.html", {"company": company})


# ── Location CRUD ──────────────────────────────────────────────────────────────

class CompanyLocationCreateView(LoginRequiredMixin, View):
    def _get_company(self, company_pk):
        return get_object_or_404(Company, pk=company_pk, deleted_at__isnull=True)

    def get(self, request, company_pk):
        company = self._get_company(company_pk)
        form = CompanyLocationAddForm()
        return render(request, "crm/companies/location_form.html", {
            "form": form, "company": company, "title": "Add Location",
        })

    def post(self, request, company_pk):
        company = self._get_company(company_pk)
        form = CompanyLocationAddForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            address = Address.objects.create(
                line1=d["line1"],
                line2=d.get("line2", ""),
                postal_code=d["postal_code"],
                city=d["city"],
                state_region=d.get("state_region", ""),
                country=d["country"],
            )
            CompanyLocation.objects.create(
                company=company,
                address=address,
                name=d["name"],
                type=d["type"],
            )
            return redirect(reverse("crm:company_detail", kwargs={"pk": company.pk}))
        return render(request, "crm/companies/location_form.html", {
            "form": form, "company": company, "title": "Add Location",
        })


class CompanyLocationUpdateView(LoginRequiredMixin, View):
    def _get_objects(self, company_pk, pk):
        company = get_object_or_404(Company, pk=company_pk, deleted_at__isnull=True)
        location = get_object_or_404(CompanyLocation, pk=pk, company=company)
        return company, location

    def get(self, request, company_pk, pk):
        company, location = self._get_objects(company_pk, pk)
        initial = {
            "name": location.name,
            "type": location.type,
            "line1": location.address.line1,
            "line2": location.address.line2,
            "postal_code": location.address.postal_code,
            "city": location.address.city,
            "state_region": location.address.state_region,
            "country": location.address.country,
        }
        form = CompanyLocationAddForm(initial=initial)
        return render(request, "crm/companies/location_form.html", {
            "form": form, "company": company, "location": location, "title": f"Edit {location.name}",
        })

    def post(self, request, company_pk, pk):
        company, location = self._get_objects(company_pk, pk)
        form = CompanyLocationAddForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            address = location.address
            address.line1 = d["line1"]
            address.line2 = d.get("line2", "")
            address.postal_code = d["postal_code"]
            address.city = d["city"]
            address.state_region = d.get("state_region", "")
            address.country = d["country"]
            address.save()
            location.name = d["name"]
            location.type = d["type"]
            location.save()
            return redirect(reverse("crm:company_detail", kwargs={"pk": company.pk}))
        return render(request, "crm/companies/location_form.html", {
            "form": form, "company": company, "location": location, "title": f"Edit {location.name}",
        })


class CompanyLocationDeleteView(LoginRequiredMixin, View):
    def post(self, request, company_pk, pk):
        company = get_object_or_404(Company, pk=company_pk, deleted_at__isnull=True)
        location = get_object_or_404(CompanyLocation, pk=pk, company=company)
        address = location.address
        location.delete()
        if not address.company_locations.exists():
            address.delete()
        return redirect(reverse("crm:company_detail", kwargs={"pk": company.pk}))


# ── Phone number CRUD ──────────────────────────────────────────────────────────

class CompanyPhoneNumberCreateView(LoginRequiredMixin, View):
    def _get_company(self, company_pk):
        return get_object_or_404(Company, pk=company_pk, deleted_at__isnull=True)

    def get(self, request, company_pk):
        company = self._get_company(company_pk)
        form = CompanyPhoneNumberAddForm()
        return render(request, "crm/companies/phone_form.html", {
            "form": form, "company": company, "title": "Add Phone Number",
        })

    def post(self, request, company_pk):
        company = self._get_company(company_pk)
        form = CompanyPhoneNumberAddForm(request.POST)
        if form.is_valid():
            phone = form.save(commit=False)
            phone.company = company
            phone.save()
            return redirect(reverse("crm:company_detail", kwargs={"pk": company.pk}))
        return render(request, "crm/companies/phone_form.html", {
            "form": form, "company": company, "title": "Add Phone Number",
        })


class CompanyPhoneNumberUpdateView(LoginRequiredMixin, View):
    def _get_objects(self, company_pk, pk):
        company = get_object_or_404(Company, pk=company_pk, deleted_at__isnull=True)
        phone = get_object_or_404(CompanyPhoneNumber, pk=pk, company=company)
        return company, phone

    def get(self, request, company_pk, pk):
        company, phone = self._get_objects(company_pk, pk)
        form = CompanyPhoneNumberAddForm(instance=phone)
        return render(request, "crm/companies/phone_form.html", {
            "form": form, "company": company, "phone": phone, "title": f"Edit {phone.phone_number}",
        })

    def post(self, request, company_pk, pk):
        company, phone = self._get_objects(company_pk, pk)
        form = CompanyPhoneNumberAddForm(request.POST, instance=phone)
        if form.is_valid():
            form.save()
            return redirect(reverse("crm:company_detail", kwargs={"pk": company.pk}))
        return render(request, "crm/companies/phone_form.html", {
            "form": form, "company": company, "phone": phone, "title": f"Edit {phone.phone_number}",
        })


class CompanyPhoneNumberDeleteView(LoginRequiredMixin, View):
    def post(self, request, company_pk, pk):
        company = get_object_or_404(Company, pk=company_pk, deleted_at__isnull=True)
        phone = get_object_or_404(CompanyPhoneNumber, pk=pk, company=company)
        phone.delete()
        return redirect(reverse("crm:company_detail", kwargs={"pk": company.pk}))
