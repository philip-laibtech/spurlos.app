from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def dashboard(request):
    stat_cards = [
        {"label": "Total Contacts", "value": "8"},
        {"label": "Active",         "value": "6"},
        {"label": "Companies",      "value": "8"},
    ]
    return render(request, "dashboard/dashboard.html", {
        "active_page": "dashboard",
        "stat_cards": stat_cards,
    })
