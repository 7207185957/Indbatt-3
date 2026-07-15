"""
URL configuration for the Unit Administration System.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.generic import RedirectView

admin.site.site_header = 'Unit Administration System'
admin.site.site_title = 'Unit Admin'
admin.site.index_title = 'Unit Structure & Account Administration'

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='dashboard:home', permanent=False)),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('admin/', admin.site.urls),
    path('dashboard/', include('dashboard.urls')),
    path('personnel/', include('personnel.urls')),
    path('absence/', include('absence.urls')),
    path('strength/', include('strength.urls')),
    path('duty/', include('dutyroster.urls')),
    path('reports/', include('reports.urls')),
    path('accounts/', include('accounts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
