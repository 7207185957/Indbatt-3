from django.contrib import admin

from .models import Appointment, Company, Platoon, Section


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')
    ordering = ('name',)


@admin.register(Platoon)
class PlatoonAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'is_active', 'updated_at')
    list_filter = ('company', 'is_active')
    search_fields = ('name', 'company__name')
    ordering = ('company__name', 'name')


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'platoon', 'is_active', 'updated_at')
    list_filter = ('platoon__company', 'is_active')
    search_fields = ('name', 'platoon__name')
    ordering = ('platoon__company__name', 'platoon__name', 'name')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
    ordering = ('name',)
