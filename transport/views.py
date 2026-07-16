from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, TemplateView

from .models import FuelEntry, MaintenanceRecord, Vehicle


class TransportDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'transport/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vehicles = Vehicle.objects.filter(is_active=True)
        context.update({
            'total_vehicles': vehicles.count(),
            'serviceable_count': vehicles.filter(status=Vehicle.STATUS_SERVICEABLE).count(),
            'unserviceable_count': vehicles.filter(status=Vehicle.STATUS_UNSERVICEABLE).count(),
            'maintenance_count': vehicles.filter(status=Vehicle.STATUS_MAINTENANCE).count(),
            'recent_maintenance': MaintenanceRecord.objects.select_related('vehicle')[:8],
            'recent_fuel': FuelEntry.objects.select_related('vehicle')[:8],
        })
        return context


class VehicleListView(LoginRequiredMixin, ListView):
    model = Vehicle
    template_name = 'transport/vehicle_list.html'
    context_object_name = 'vehicles'
    paginate_by = 25

    def get_queryset(self):
        queryset = Vehicle.objects.filter(is_active=True)
        status = self.request.GET.get('status', '').strip()
        q = self.request.GET.get('q', '').strip()
        if status:
            queryset = queryset.filter(status=status)
        if q:
            queryset = queryset.filter(registration_number__icontains=q)
        return queryset
