from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def settings(request):
    return render(request, 'accounts/settings.html')
