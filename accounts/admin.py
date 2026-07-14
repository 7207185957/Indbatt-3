from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class UnitUserAdmin(UserAdmin):
    """
    Admin registration for the custom User model. Super Admins manage
    individual accounts here, including role and company assignment.
    """

    fieldsets = UserAdmin.fieldsets + (
        ('Unit Administration System', {
            'fields': ('role', 'company', 'rank', 'service_number', 'contact_number', 'is_active_account'),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Unit Administration System', {
            'fields': ('role', 'company', 'rank', 'service_number', 'contact_number'),
        }),
    )
    list_display = ('username', 'get_full_name', 'role', 'company', 'is_active', 'is_staff')
    list_filter = ('role', 'company', 'is_active', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'service_number')
