from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import DetailView, ListView, View

from activities.forms import ActivityForm
from activities.models import Activity
from activities.selectors import get_activity_detail, get_activity_list, search_activities
from activities.services import archive_activity, create_activity, update_activity


class ActivityListView(LoginRequiredMixin, ListView):
    template_name = "activities/list.html"
    context_object_name = "activities"

    def get_queryset(self):
        q = self.request.GET.get("q", "").strip()
        qs = search_activities(q) if q else get_activity_list()
        activity_type = self.request.GET.get("type", "").strip()
        if activity_type:
            qs = qs.filter(activity_type=activity_type)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["query"] = self.request.GET.get("q", "")
        ctx["selected_type"] = self.request.GET.get("type", "")
        ctx["activity_types"] = Activity.ActivityType.choices
        return ctx


class ActivityDetailView(LoginRequiredMixin, DetailView):
    template_name = "activities/detail.html"
    context_object_name = "activity"

    def get_object(self):
        return get_activity_detail(self.kwargs["pk"])


class ActivityCreateView(LoginRequiredMixin, View):
    template_name = "activities/form.html"

    def get(self, request):
        initial = {}
        contact_pk = request.GET.get("contact")
        company_pk = request.GET.get("company")
        project_pk = request.GET.get("project")
        if contact_pk:
            initial["contact"] = contact_pk
        if company_pk:
            initial["company"] = company_pk
        if project_pk:
            initial["project"] = project_pk
        form = ActivityForm(initial=initial)
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = ActivityForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            activity = create_activity(
                company=d["company"],
                title=d["title"],
                contact=d.get("contact"),
                project=d.get("project"),
                activity_type=d.get("activity_type", ""),
                description=d.get("description", ""),
                occurred_at=d.get("occurred_at"),
                created_by=request.user if request.user.is_authenticated else None,
            )
            return redirect(reverse("activities:activity_detail", kwargs={"pk": activity.pk}))
        return render(request, self.template_name, {"form": form})


class ActivityUpdateView(LoginRequiredMixin, View):
    template_name = "activities/form.html"

    def _get_activity(self, pk):
        return get_object_or_404(Activity, pk=pk, deleted_at__isnull=True)

    def get(self, request, pk):
        activity = self._get_activity(pk)
        form = ActivityForm(instance=activity)
        return render(request, self.template_name, {"form": form, "object": activity})

    def post(self, request, pk):
        activity = self._get_activity(pk)
        form = ActivityForm(request.POST, instance=activity)
        if form.is_valid():
            update_activity(activity, **form.cleaned_data)
            return redirect(reverse("activities:activity_detail", kwargs={"pk": activity.pk}))
        return render(request, self.template_name, {"form": form, "object": activity})


class ActivityDeleteView(LoginRequiredMixin, View):
    template_name = "activities/confirm_delete.html"

    def _get_activity(self, pk):
        return get_object_or_404(Activity, pk=pk, deleted_at__isnull=True)

    def get(self, request, pk):
        activity = self._get_activity(pk)
        return render(request, self.template_name, {"activity": activity})

    def post(self, request, pk):
        activity = self._get_activity(pk)
        archive_activity(activity)
        return redirect(reverse("activities:activity_list"))
