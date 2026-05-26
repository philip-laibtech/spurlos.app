from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View

from projects.forms import ProjectForm
from projects.models import Project
from projects.selectors import get_project_detail, get_project_list, search_projects
from projects.services import archive_project, create_project, update_project


class ProjectListView(LoginRequiredMixin, ListView):
    template_name = "projects/list.html"
    context_object_name = "projects"

    def get_queryset(self):
        q = self.request.GET.get("q", "").strip()
        if q:
            return search_projects(q)
        return get_project_list()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["query"] = self.request.GET.get("q", "")
        return ctx


class ProjectDetailView(LoginRequiredMixin, DetailView):
    template_name = "projects/detail.html"
    context_object_name = "project"

    def get_object(self):
        return get_project_detail(self.kwargs["pk"])


class ProjectCreateView(LoginRequiredMixin, View):
    template_name = "projects/form.html"

    def get(self, request):
        form = ProjectForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = ProjectForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            project = create_project(
                company=d["company"],
                title=d["title"],
                contact=d.get("contact"),
            )
            return redirect(reverse("projects:project_detail", kwargs={"pk": project.pk}))
        return render(request, self.template_name, {"form": form})


class ProjectUpdateView(LoginRequiredMixin, View):
    template_name = "projects/form.html"

    def _get_project(self, pk):
        return get_object_or_404(Project, pk=pk, deleted_at__isnull=True)

    def get(self, request, pk):
        project = self._get_project(pk)
        form = ProjectForm(instance=project)
        return render(request, self.template_name, {"form": form, "object": project})

    def post(self, request, pk):
        project = self._get_project(pk)
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            update_project(project, **form.cleaned_data)
            return redirect(reverse("projects:project_detail", kwargs={"pk": project.pk}))
        return render(request, self.template_name, {"form": form, "object": project})


class ProjectDeleteView(LoginRequiredMixin, View):
    template_name = "projects/confirm_delete.html"

    def _get_project(self, pk):
        return get_object_or_404(Project, pk=pk, deleted_at__isnull=True)

    def get(self, request, pk):
        project = self._get_project(pk)
        return render(request, self.template_name, {"project": project})

    def post(self, request, pk):
        project = self._get_project(pk)
        archive_project(project)
        return redirect(reverse("projects:project_list"))
