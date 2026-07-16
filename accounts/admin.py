from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class UnitUserAdmin(UserAdmin):
    """Admin registration for individually attributable user accounts."""

    fieldsets = UserAdmin.fieldsets + (
        ('Unit Administration System', {
            'fields': (
                'role', 'company', 'rank', 'appointment', 'service_number',
                'contact_number', 'profile_photo',
            ),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Unit Administration System', {
            'fields': (
                'role', 'company', 'rank', 'appointment', 'service_number',
                'contact_number', 'profile_photo',
            ),
        }),
    )
    list_display = ('username', 'get_full_name', 'rank', 'appointment', 'role', 'company', 'is_active', 'is_staff')
    list_filter = ('role', 'company', 'is_active', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'service_number', 'appointment')
