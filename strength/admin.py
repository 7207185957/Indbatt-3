from django.contrib import admin

from .models import DailyStrength


@admin.register(DailyStrength)
class DailyStrengthAdmin(admin.ModelAdmin):
    list_display = ('date', 'company', 'total_posted_strength', 'present', 'total_absent')
    list_filter = ('company', 'date')
    search_fields = ('company__name',)
    ordering = ('-date', 'company__name')

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
