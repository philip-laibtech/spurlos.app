from django.conf import settings
from django.conf.urls.static import static
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
    path('crm/', include('crm.urls', namespace='crm')),
    path('projects/', include('projects.urls', namespace='projects')),
    path('tasks/', include('tasks.urls', namespace='tasks')),
    path('documents/', include('documents.urls', namespace='documents')),
    path('activities/', include('activities.urls', namespace='activities')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
