from django.urls import path

from . import views

app_name = 'transport'

urlpatterns = [
    path('', views.TransportDashboardView.as_view(), name='dashboard'),
    path('vehicles/', views.VehicleListView.as_view(), name='vehicle_list'),
]
