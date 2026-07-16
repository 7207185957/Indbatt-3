from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.UnitDashboardView.as_view(), name='home'),
    path('manpower/', views.ManpowerDashboardView.as_view(), name='manpower'),
    path('module/<slug:module_slug>/', views.ModuleDashboardView.as_view(), name='module'),
]
