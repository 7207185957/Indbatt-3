from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import Http404
from django.utils import timezone
from django.views.generic import TemplateView

from absence.models import AbsenceRecord
from core.roles import accessible_company_ids, can_edit_records
from dutyroster.models import DutyRoster
from personnel.models import Personnel
from unitstructure.models import Company

from .models import DashboardAnnouncement, DashboardHeroSlide, UnitEvent


MODULE_WORKSPACES = {
    'transport': {
        'name': 'Transport',
        'icon': '▣',
        'summary': 'Administrative workspace for transport records and availability.',
        'sections': ['Dashboard', 'Register', 'Availability', 'Maintenance', 'Fuel Records', 'Reports'],
    },
    'stores': {
        'name': 'Stores',
        'icon': '▤',
        'summary': 'Administrative workspace for stock, receipts, issues and reports.',
        'sections': ['Dashboard', 'Stock Register', 'Receipts and Issues', 'Demands', 'Deficiencies', 'Reports'],
    },
    'training': {
        'name': 'Training',
        'icon': '◎',
        'summary': 'Administrative workspace for schedules, attendance and results.',
        'sections': ['Dashboard', 'Calendar', 'Attendance', 'Results', 'Certificates', 'Reports'],
    },
    'medical': {
        'name': 'Medical',
        'icon': '✚',
        'summary': 'Administrative workspace for non-sensitive medical returns and inspections.',
        'sections': ['Dashboard', 'Sick Report', 'Hospital Records', 'Inspections', 'Due Actions', 'Reports'],
    },
    'administration': {
        'name': 'Administration',
        'icon': '▦',
        'summary': 'Unit notices, events, returns and system administration.',
        'sections': ['Dashboard', 'Announcements', 'Events', 'Pending Returns', 'User Accounts', 'System Admin'],
    },
}


class UnitDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/unit_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        today = timezone.localdate()
        company_ids = accessible_company_ids(user)

        personnel_qs = Personnel.objects.filter(is_active=True)
        absence_qs = AbsenceRecord.objects.filter(
            from_date__lte=today,
            to_date__gte=today,
        ).exclude(status__in=[AbsenceRecord.STATUS_RETURNED, AbsenceRecord.STATUS_CANCELLED])
        duty_qs = DutyRoster.objects.filter(duty_date=today)

        if company_ids is not None:
            personnel_qs = personnel_qs.filter(company_id__in=company_ids)
            absence_qs = absence_qs.filter(person__company_id__in=company_ids)
            duty_qs = duty_qs.filter(company_id__in=company_ids)

        total_active = personnel_qs.count()
        present_count = personnel_qs.filter(status=Personnel.STATUS_PRESENT).count()

        announcement_q = Q(is_active=True) & (Q(starts_on__isnull=True) | Q(starts_on__lte=today)) & (Q(ends_on__isnull=True) | Q(ends_on__gte=today))
        announcements = DashboardAnnouncement.objects.filter(announcement_q)[:8]
        events_qs = UnitEvent.objects.filter(
            is_active=True,
            event_date__gte=today,
            event_date__lte=today + timedelta(days=30),
        )
        if company_ids is not None:
            events_qs = events_qs.filter(Q(company__isnull=True) | Q(company_id__in=company_ids))

        context.update({
            'total_active': total_active,
            'present_count': present_count,
            'current_absence_count': absence_qs.count(),
            'today_duty_count': duty_qs.count(),
            'announcements': announcements,
            'upcoming_events': events_qs.select_related('company')[:8],
            'today': today,
            'is_scoped': company_ids is not None,
        })
        return context


class ManpowerDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        today = timezone.localdate()
        company_ids = accessible_company_ids(user)

        personnel_qs = Personnel.objects.filter(is_active=True)
        companies_qs = Company.objects.filter(is_active=True)
        absence_qs = AbsenceRecord.objects.filter(
            from_date__lte=today, to_date__gte=today,
        ).exclude(status__in=[AbsenceRecord.STATUS_RETURNED, AbsenceRecord.STATUS_CANCELLED])
        duty_qs = DutyRoster.objects.filter(duty_date=today)

        if company_ids is not None:
            personnel_qs = personnel_qs.filter(company_id__in=company_ids)
            companies_qs = companies_qs.filter(pk__in=company_ids)
            absence_qs = absence_qs.filter(person__company_id__in=company_ids)
            duty_qs = duty_qs.filter(company_id__in=company_ids)

        total_active = personnel_qs.count()
        present_count = personnel_qs.filter(status=Personnel.STATUS_PRESENT).count()
        leave_count = personnel_qs.filter(status=Personnel.STATUS_LEAVE).count()
        td_course_count = personnel_qs.filter(status__in=[Personnel.STATUS_TD, Personnel.STATUS_COURSE]).count()
        absent_count = total_active - present_count

        company_summary = []
        for company in companies_qs.order_by('name'):
            company_personnel = personnel_qs.filter(company=company)
            company_summary.append({
                'company': company,
                'total': company_personnel.count(),
                'present': company_personnel.filter(status=Personnel.STATUS_PRESENT).count(),
                'leave': company_personnel.filter(status=Personnel.STATUS_LEAVE).count(),
                'td': company_personnel.filter(status=Personnel.STATUS_TD).count(),
                'course': company_personnel.filter(status=Personnel.STATUS_COURSE).count(),
                'hospital': company_personnel.filter(status=Personnel.STATUS_HOSPITAL).count(),
                'attached_out': company_personnel.filter(status=Personnel.STATUS_ATTACHED_OUT).count(),
            })

        announcement_q = Q(is_active=True) & (Q(starts_on__isnull=True) | Q(starts_on__lte=today)) & (Q(ends_on__isnull=True) | Q(ends_on__gte=today))
        announcements = DashboardAnnouncement.objects.filter(announcement_q)[:8]
        hero_slides = DashboardHeroSlide.objects.filter(is_active=True)[:5]

        events_qs = UnitEvent.objects.filter(
            is_active=True,
            event_date__gte=today,
            event_date__lte=today + timedelta(days=30),
        )
        if company_ids is not None:
            events_qs = events_qs.filter(Q(company__isnull=True) | Q(company_id__in=company_ids))

        context.update({
            'total_active': total_active,
            'present_count': present_count,
            'absent_count': absent_count,
            'leave_count': leave_count,
            'td_course_count': td_course_count,
            'company_summary': company_summary,
            'upcoming_returns': absence_qs.select_related('person', 'person__company').order_by('to_date')[:8],
            'today_duties': duty_qs.select_related('company').prefetch_related('personnel_detailed')[:8],
            'recent_personnel': personnel_qs.order_by('-updated_at')[:5],
            'recent_absence': absence_qs.order_by('-updated_at')[:5],
            'announcements': announcements,
            'hero_slides': hero_slides,
            'upcoming_events': events_qs.select_related('company')[:8],
            'today': today,
            'can_edit': can_edit_records(user),
            'is_scoped': company_ids is not None,
        })
        return context


class ModuleDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/module_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        module_slug = kwargs.get('module_slug')
        module = MODULE_WORKSPACES.get(module_slug)
        if module is None:
            raise Http404('Module not found')

        context.update({
            'module_slug': module_slug,
            'module': module,
            'today': timezone.localdate(),
            'announcements': DashboardAnnouncement.objects.filter(is_active=True)[:5],
            'upcoming_events': UnitEvent.objects.filter(
                is_active=True,
                event_date__gte=timezone.localdate(),
            ).select_related('company')[:5],
        })
        return context


DashboardView = UnitDashboardView
