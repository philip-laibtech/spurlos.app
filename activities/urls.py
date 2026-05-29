from django.urls import path

from activities.views.activities import (
    ActivityCreateView,
    ActivityDeleteView,
    ActivityDetailView,
    ActivityListView,
    ActivityUpdateView,
)

app_name = "activities"

urlpatterns = [
    path("", ActivityListView.as_view(), name="activity_list"),
    path("create/", ActivityCreateView.as_view(), name="activity_create"),
    path("<int:pk>/", ActivityDetailView.as_view(), name="activity_detail"),
    path("<int:pk>/edit/", ActivityUpdateView.as_view(), name="activity_update"),
    path("<int:pk>/delete/", ActivityDeleteView.as_view(), name="activity_delete"),
]
