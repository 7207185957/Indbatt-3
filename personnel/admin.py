from django.contrib import admin

from .models import Personnel


@admin.register(Personnel)
class PersonnelAdmin(admin.ModelAdmin):
    list_display = ('army_number', 'rank', 'full_name', 'company', 'platoon', 'status', 'is_active')
    list_filter = ('company', 'status', 'is_active', 'platoon')
    search_fields = ('army_number', 'full_name', 'rank')
    autocomplete_fields = ('company', 'platoon', 'section', 'appointment')
    ordering = ('company__name', 'rank', 'full_name')

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
