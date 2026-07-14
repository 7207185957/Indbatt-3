from django.contrib import admin

from .models import DutyRoster


@admin.register(DutyRoster)
class DutyRosterAdmin(admin.ModelAdmin):
    list_display = ('duty_date', 'duty_type', 'company', 'shift_time', 'status')
    list_filter = ('company', 'status', 'duty_type')
    search_fields = ('duty_type', 'duty_location')
    autocomplete_fields = ('company',)
    filter_horizontal = ('personnel_detailed',)
    ordering = ('-duty_date',)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
