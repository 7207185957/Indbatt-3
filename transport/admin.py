from django.contrib import admin

from .models import FuelEntry, MaintenanceRecord, Vehicle


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('registration_number', 'vehicle_type', 'make_model', 'status', 'location', 'is_active')
    list_filter = ('status', 'is_active', 'vehicle_type')
    search_fields = ('registration_number', 'vehicle_type', 'make_model', 'location')


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'reported_on', 'issue', 'completed_on', 'cost')
    list_filter = ('reported_on', 'completed_on')
    search_fields = ('vehicle__registration_number', 'issue', 'action_taken')


@admin.register(FuelEntry)
class FuelEntryAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'entry_date', 'quantity_litres', 'odometer')
    list_filter = ('entry_date',)
    search_fields = ('vehicle__registration_number', 'remarks')
