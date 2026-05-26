from django.urls import path

from projects.views.projects import (
    ProjectCreateView,
    ProjectDeleteView,
    ProjectDetailView,
    ProjectListView,
    ProjectUpdateView,
)

app_name = "projects"

urlpatterns = [
    path("", ProjectListView.as_view(), name="project_list"),
    path("create/", ProjectCreateView.as_view(), name="project_create"),
    path("<int:pk>/", ProjectDetailView.as_view(), name="project_detail"),
    path("<int:pk>/edit/", ProjectUpdateView.as_view(), name="project_update"),
    path("<int:pk>/delete/", ProjectDeleteView.as_view(), name="project_delete"),
]
