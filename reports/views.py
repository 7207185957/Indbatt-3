import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic import TemplateView, View

from absence.models import AbsenceRecord
from core.roles import accessible_company_ids
from dutyroster.models import DutyRoster
from personnel.models import Personnel
from unitstructure.models import Company

from .filters import (
    absence_report_queryset,
    due_to_return_report_queryset,
    duty_report_queryset,
    personnel_report_queryset,
    strength_report_queryset,
)
from .utils import export_csv


def _visible_companies(user):
    company_ids = accessible_company_ids(user)
    companies = Company.objects.filter(is_active=True)
    if company_ids is not None:
        companies = companies.filter(pk__in=company_ids)
    return companies


class ReportsHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/reports_home.html'


class PersonnelReportView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/personnel_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['personnel_list'] = personnel_report_queryset(self.request.user, self.request.GET)
        context['companies'] = _visible_companies(self.request.user)
        context['status_choices'] = Personnel.STATUS_CHOICES
        context['selected_company'] = self.request.GET.get('company', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_active'] = self.request.GET.get('active', 'active')
        return context


class PersonnelReportExportView(LoginRequiredMixin, View):
    def get(self, request):
        queryset = personnel_report_queryset(request.user, request.GET)
        headers = [
            'Army Number', 'Rank', 'Full Name', 'Company', 'Platoon', 'Section',
            'Appointment', 'Date of Joining', 'Status', 'Active',
        ]
        rows = (
            [
                p.army_number, p.rank, p.full_name, p.company.name,
                p.platoon.name if p.platoon else '', p.section.name if p.section else '',
                p.appointment.name if p.appointment else '', p.date_of_joining_unit,
                p.get_status_display(), 'Yes' if p.is_active else 'No',
            ]
            for p in queryset
        )
        return export_csv('personnel_report.csv', headers, rows)


class StrengthReportView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/strength_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['strength_list'] = strength_report_queryset(self.request.user, self.request.GET)
        context['companies'] = _visible_companies(self.request.user)
        context['selected_company'] = self.request.GET.get('company', '')
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')
        return context


class StrengthReportExportView(LoginRequiredMixin, View):
    def get(self, request):
        queryset = strength_report_queryset(request.user, request.GET)
        headers = [
            'Date', 'Company', 'Total Posted', 'Present', 'Leave', 'Temporary Duty',
            'Course', 'Hospital/Sick', 'Attached Out', 'Other Absence', 'Total Absent',
        ]
        rows = (
            [
                s.date, s.company.name, s.total_posted_strength, s.present, s.leave,
                s.temporary_duty, s.course, s.hospital_sick, s.attached_out,
                s.other_absence, s.total_absent,
            ]
            for s in queryset
        )
        return export_csv('strength_report.csv', headers, rows)


class AbsenceReportView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/absence_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['absence_list'] = absence_report_queryset(self.request.user, self.request.GET)
        context['companies'] = _visible_companies(self.request.user)
        context['type_choices'] = AbsenceRecord.TYPE_CHOICES
        context['status_choices'] = AbsenceRecord.STATUS_CHOICES
        context['selected_company'] = self.request.GET.get('company', '')
        context['selected_type'] = self.request.GET.get('type', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')
        return context


class AbsenceReportExportView(LoginRequiredMixin, View):
    def get(self, request):
        queryset = absence_report_queryset(request.user, request.GET)
        headers = [
            'Army Number', 'Name', 'Company', 'Type', 'From Date', 'To Date',
            'Authority/Reference', 'Destination', 'Status',
        ]
        rows = (
            [
                a.person.army_number, a.person.full_name, a.person.company.name,
                a.get_type_display(), a.from_date, a.to_date, a.authority_reference,
                a.destination, a.get_status_display(),
            ]
            for a in queryset
        )
        return export_csv('absence_report.csv', headers, rows)


class DutyReportView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/duty_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['duty_list'] = duty_report_queryset(self.request.user, self.request.GET)
        context['companies'] = _visible_companies(self.request.user)
        context['status_choices'] = DutyRoster.STATUS_CHOICES
        context['selected_company'] = self.request.GET.get('company', '')
        context['selected_duty_type'] = self.request.GET.get('duty_type', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')
        return context


class DutyReportExportView(LoginRequiredMixin, View):
    def get(self, request):
        queryset = duty_report_queryset(request.user, request.GET)
        headers = ['Date', 'Duty Type', 'Company', 'Personnel Detailed', 'Location/Post', 'Shift/Time', 'Status']
        rows = (
            [
                d.duty_date, d.duty_type, d.company.name,
                ', '.join(p.full_name for p in d.personnel_detailed.all()),
                d.duty_location, d.shift_time, d.get_status_display(),
            ]
            for d in queryset
        )
        return export_csv('duty_roster_report.csv', headers, rows)


class DueToReturnReportView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/due_to_return_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        days = int(self.request.GET.get('days', 7))
        horizon_date = today + datetime.timedelta(days=days)
        context['absence_list'] = due_to_return_report_queryset(self.request.user, self.request.GET, today, horizon_date)
        context['companies'] = _visible_companies(self.request.user)
        context['selected_company'] = self.request.GET.get('company', '')
        context['days'] = days
        return context


class DueToReturnReportExportView(LoginRequiredMixin, View):
    def get(self, request):
        today = timezone.localdate()
        days = int(request.GET.get('days', 7))
        horizon_date = today + datetime.timedelta(days=days)
        queryset = due_to_return_report_queryset(request.user, request.GET, today, horizon_date)
        headers = ['Army Number', 'Name', 'Company', 'Type', 'From Date', 'To Date', 'Status']
        rows = (
            [
                a.person.army_number, a.person.full_name, a.person.company.name,
                a.get_type_display(), a.from_date, a.to_date, a.get_status_display(),
            ]
            for a in queryset
        )
        return export_csv('due_to_return_report.csv', headers, rows)
