from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='dashboard', permanent=False)),
    path('admin/auth/user/', RedirectView.as_view(url='/admin/accounts/user/', permanent=True)),
    path('admin/auth/user/<path:rest>', RedirectView.as_view(url='/admin/accounts/user/%(rest)s', permanent=True)),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
]
