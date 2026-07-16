from django.conf import settings
from django.db import models


class Vehicle(models.Model):
    STATUS_SERVICEABLE = 'SERVICEABLE'
    STATUS_UNSERVICEABLE = 'UNSERVICEABLE'
    STATUS_MAINTENANCE = 'MAINTENANCE'
    STATUS_CHOICES = [
        (STATUS_SERVICEABLE, 'Serviceable'),
        (STATUS_UNSERVICEABLE, 'Unserviceable'),
        (STATUS_MAINTENANCE, 'Under maintenance'),
    ]

    registration_number = models.CharField(max_length=40, unique=True)
    vehicle_type = models.CharField(max_length=80)
    make_model = models.CharField(max_length=120, blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SERVICEABLE)
    location = models.CharField(max_length=120, blank=True)
    remarks = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='transport_vehicles_created')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='transport_vehicles_updated')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['registration_number']

    def __str__(self):
        return f'{self.registration_number} - {self.vehicle_type}'


class MaintenanceRecord(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='maintenance_records')
    reported_on = models.DateField()
    issue = models.CharField(max_length=200)
    action_taken = models.TextField(blank=True)
    completed_on = models.DateField(null=True, blank=True)
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-reported_on']

    def __str__(self):
        return f'{self.vehicle.registration_number} - {self.reported_on}'


class FuelEntry(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='fuel_entries')
    entry_date = models.DateField()
    quantity_litres = models.DecimalField(max_digits=10, decimal_places=2)
    odometer = models.PositiveIntegerField(null=True, blank=True)
    remarks = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-entry_date']

    def __str__(self):
        return f'{self.vehicle.registration_number} - {self.quantity_litres} L'
