from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import DetailView, ListView, View

from tasks.forms import TaskForm
from tasks.models import Task
from tasks.selectors import get_task_detail, get_task_list, search_tasks
from tasks.services import archive_task, create_task, update_task


class TaskListView(LoginRequiredMixin, ListView):
    template_name = "tasks/list.html"
    context_object_name = "tasks"

    def get_queryset(self):
        q = self.request.GET.get("q", "").strip()
        if q:
            return search_tasks(q)
        return get_task_list()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["query"] = self.request.GET.get("q", "")
        return ctx


class TaskDetailView(LoginRequiredMixin, DetailView):
    template_name = "tasks/detail.html"
    context_object_name = "task"

    def get_object(self):
        return get_task_detail(self.kwargs["pk"])


class TaskCreateView(LoginRequiredMixin, View):
    template_name = "tasks/form.html"

    def _safe_next(self, request, url):
        if url and url_has_allowed_host_and_scheme(url, allowed_hosts={request.get_host()}):
            return url
        return None

    def get(self, request):
        initial = {}
        project_pk = request.GET.get("project")
        if project_pk:
            initial["project"] = project_pk
        form = TaskForm(initial=initial)
        next_url = self._safe_next(request, request.GET.get("next"))
        return render(request, self.template_name, {"form": form, "next": next_url})

    def post(self, request):
        form = TaskForm(request.POST)
        next_url = self._safe_next(request, request.POST.get("next"))
        if form.is_valid():
            d = form.cleaned_data
            task = create_task(
                project=d["project"],
                title=d["title"],
                assigned_user=d.get("assigned_user"),
                description=d.get("description", ""),
                due_date=d.get("due_date"),
                status=d.get("status", ""),
                priority=d.get("priority", ""),
            )
            return redirect(next_url or reverse("tasks:task_detail", kwargs={"pk": task.pk}))
        return render(request, self.template_name, {"form": form, "next": next_url})


class TaskUpdateView(LoginRequiredMixin, View):
    template_name = "tasks/form.html"

    def _get_task(self, pk):
        return get_object_or_404(Task, pk=pk, deleted_at__isnull=True)

    def get(self, request, pk):
        task = self._get_task(pk)
        form = TaskForm(instance=task)
        return render(request, self.template_name, {"form": form, "object": task})

    def post(self, request, pk):
        task = self._get_task(pk)
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            update_task(task, **form.cleaned_data)
            return redirect(reverse("tasks:task_detail", kwargs={"pk": task.pk}))
        return render(request, self.template_name, {"form": form, "object": task})


class TaskDeleteView(LoginRequiredMixin, View):
    template_name = "tasks/confirm_delete.html"

    def _get_task(self, pk):
        return get_object_or_404(Task, pk=pk, deleted_at__isnull=True)

    def get(self, request, pk):
        task = self._get_task(pk)
        return render(request, self.template_name, {"task": task})

    def post(self, request, pk):
        task = self._get_task(pk)
        archive_task(task)
        return redirect(reverse("tasks:task_list"))
