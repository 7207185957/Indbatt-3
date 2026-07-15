from django.contrib import admin

from .models import DashboardAnnouncement, DashboardHeroSlide, UnitEvent


@admin.register(DashboardAnnouncement)
class DashboardAnnouncementAdmin(admin.ModelAdmin):
    list_display = ('message', 'priority', 'is_active', 'starts_on', 'ends_on', 'order')
    list_filter = ('priority', 'is_active')
    search_fields = ('message',)
    list_editable = ('is_active', 'order')


@admin.register(DashboardHeroSlide)
class DashboardHeroSlideAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    search_fields = ('title', 'subtitle')


@admin.register(UnitEvent)
class UnitEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_type', 'event_date', 'company', 'is_active')
    list_filter = ('event_type', 'event_date', 'company', 'is_active')
    search_fields = ('title', 'description')
