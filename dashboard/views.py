from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic import TemplateView

from absence.models import AbsenceRecord
from core.roles import accessible_company_ids, can_edit_records
from dutyroster.models import DutyRoster
from personnel.models import Personnel
from strength.models import DailyStrength
from unitstructure.models import Company


class DashboardView(LoginRequiredMixin, TemplateView):
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

        upcoming_returns = absence_qs.select_related('person', 'person__company').order_by('to_date')[:8]
        today_duties = duty_qs.select_related('company').prefetch_related('personnel_detailed')[:8]

        recent_personnel = personnel_qs.order_by('-updated_at')[:5]
        recent_absence = absence_qs.order_by('-updated_at')[:5]

        context.update({
            'total_active': total_active,
            'present_count': present_count,
            'absent_count': absent_count,
            'leave_count': leave_count,
            'td_course_count': td_course_count,
            'company_summary': company_summary,
            'upcoming_returns': upcoming_returns,
            'today_duties': today_duties,
            'recent_personnel': recent_personnel,
            'recent_absence': recent_absence,
            'today': today,
            'can_edit': can_edit_records(user),
            'is_scoped': company_ids is not None,
        })
        return context
