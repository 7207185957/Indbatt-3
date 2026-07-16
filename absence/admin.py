from django.contrib import admin

from .models import AbsenceRecord


@admin.register(AbsenceRecord)
class AbsenceRecordAdmin(admin.ModelAdmin):
    list_display = ('person', 'type', 'from_date', 'to_date', 'status')
    list_filter = ('type', 'status', 'person__company')
    search_fields = ('person__full_name', 'person__army_number', 'authority_reference')
    autocomplete_fields = ('person',)
    ordering = ('-from_date',)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
