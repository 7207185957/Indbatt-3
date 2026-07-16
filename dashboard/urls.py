from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.UnitDashboardView.as_view(), name='home'),
    path('manpower/', views.ManpowerDashboardView.as_view(), name='manpower'),
]
