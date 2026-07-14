from django.contrib import messages
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from core.mixins import (
    AuditFieldsMixin,
    CompanyScopedFormMixin,
    CompanyScopedQuerysetMixin,
    EditRequiredMixin,
    ObjectCompanyPermissionMixin,
    PersonnelDetailedScopedFormMixin,
)
from core.roles import accessible_company_ids
from unitstructure.models import Company

from .forms import DutyRosterForm
from .models import DutyRoster


class DutyRosterListView(CompanyScopedQuerysetMixin, ListView):
    model = DutyRoster
    template_name = 'dutyroster/duty_list.html'
    context_object_name = 'duty_list'
    paginate_by = 25

    def get_queryset(self):
        queryset = super().get_queryset().select_related('company').prefetch_related('personnel_detailed').distinct()
        company = self.request.GET.get('company', '').strip()
        duty_type = self.request.GET.get('duty_type', '').strip()
        status = self.request.GET.get('status', '').strip()
        date_from = self.request.GET.get('date_from', '').strip()
        date_to = self.request.GET.get('date_to', '').strip()

        if company:
            queryset = queryset.filter(company_id=company)
        if duty_type:
            queryset = queryset.filter(duty_type__icontains=duty_type)
        if status:
            queryset = queryset.filter(status=status)
        if date_from:
            queryset = queryset.filter(duty_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(duty_date__lte=date_to)
        return queryset.order_by('-duty_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        company_ids = accessible_company_ids(user)
        companies = Company.objects.filter(is_active=True)
        if company_ids is not None:
            companies = companies.filter(pk__in=company_ids)
        context['companies'] = companies
        context['status_choices'] = DutyRoster.STATUS_CHOICES
        context['selected_company'] = self.request.GET.get('company', '')
        context['selected_duty_type'] = self.request.GET.get('duty_type', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')
        return context


class UpcomingDutyListView(CompanyScopedQuerysetMixin, ListView):
    model = DutyRoster
    template_name = 'dutyroster/duty_upcoming.html'
    context_object_name = 'duty_list'
    paginate_by = 25

    def get_queryset(self):
        queryset = super().get_queryset().select_related('company').prefetch_related('personnel_detailed').distinct()
        today = timezone.localdate()
        return queryset.filter(
            duty_date__gte=today, status=DutyRoster.STATUS_SCHEDULED,
        ).order_by('duty_date')


class DutyRosterDetailView(CompanyScopedQuerysetMixin, ObjectCompanyPermissionMixin, DetailView):
    model = DutyRoster
    template_name = 'dutyroster/duty_detail.html'
    context_object_name = 'duty'


class DutyRosterCreateView(
    EditRequiredMixin, CompanyScopedFormMixin, PersonnelDetailedScopedFormMixin, AuditFieldsMixin, CreateView
):
    model = DutyRoster
    form_class = DutyRosterForm
    template_name = 'dutyroster/duty_form.html'

    def get_initial(self):
        initial = super().get_initial()
        initial['duty_date'] = timezone.localdate()
        return initial

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Duty roster entry created.')
        return response


class DutyRosterUpdateView(
    EditRequiredMixin, CompanyScopedFormMixin, PersonnelDetailedScopedFormMixin,
    ObjectCompanyPermissionMixin, AuditFieldsMixin, UpdateView
):
    model = DutyRoster
    form_class = DutyRosterForm
    template_name = 'dutyroster/duty_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Duty roster entry updated.')
        return response
