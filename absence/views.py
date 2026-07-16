import datetime

from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from core.mixins import (
    AuditFieldsMixin,
    CompanyScopedQuerysetMixin,
    EditRequiredMixin,
    ObjectPersonCompanyPermissionMixin,
    PersonCompanyScopedFormMixin,
)
from core.roles import accessible_company_ids
from unitstructure.models import Company

from .forms import AbsenceRecordForm
from .models import AbsenceRecord


class AbsenceListView(CompanyScopedQuerysetMixin, ListView):
    model = AbsenceRecord
    template_name = 'absence/absence_list.html'
    context_object_name = 'absence_list'
    paginate_by = 25
    company_field_name = 'person__company'

    def get_queryset(self):
        queryset = super().get_queryset().select_related('person', 'person__company')
        q = self.request.GET.get('q', '').strip()
        company = self.request.GET.get('company', '').strip()
        type_ = self.request.GET.get('type', '').strip()
        status = self.request.GET.get('status', '').strip()
        date_from = self.request.GET.get('date_from', '').strip()
        date_to = self.request.GET.get('date_to', '').strip()
        currently_absent = self.request.GET.get('currently_absent', '').strip()

        if q:
            queryset = queryset.filter(Q(person__full_name__icontains=q) | Q(person__army_number__icontains=q))
        if company:
            queryset = queryset.filter(person__company_id=company)
        if type_:
            queryset = queryset.filter(type=type_)
        if status:
            queryset = queryset.filter(status=status)
        if date_from:
            queryset = queryset.filter(to_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(from_date__lte=date_to)
        if currently_absent == '1':
            today = timezone.localdate()
            queryset = queryset.filter(
                from_date__lte=today, to_date__gte=today,
            ).exclude(status__in=[AbsenceRecord.STATUS_RETURNED, AbsenceRecord.STATUS_CANCELLED])
        return queryset.order_by('-from_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        company_ids = accessible_company_ids(user)
        companies = Company.objects.filter(is_active=True)
        if company_ids is not None:
            companies = companies.filter(pk__in=company_ids)
        context['companies'] = companies
        context['type_choices'] = AbsenceRecord.TYPE_CHOICES
        context['status_choices'] = AbsenceRecord.STATUS_CHOICES
        context['q'] = self.request.GET.get('q', '')
        context['selected_company'] = self.request.GET.get('company', '')
        context['selected_type'] = self.request.GET.get('type', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')
        context['currently_absent'] = self.request.GET.get('currently_absent', '')
        context['today'] = timezone.localdate()
        return context


class AbsenceDetailView(CompanyScopedQuerysetMixin, ObjectPersonCompanyPermissionMixin, DetailView):
    model = AbsenceRecord
    template_name = 'absence/absence_detail.html'
    context_object_name = 'absence'
    company_field_name = 'person__company'


class AbsenceCreateView(EditRequiredMixin, PersonCompanyScopedFormMixin, AuditFieldsMixin, CreateView):
    model = AbsenceRecord
    form_class = AbsenceRecordForm
    template_name = 'absence/absence_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Absence record created.')
        return response


class AbsenceUpdateView(
    EditRequiredMixin, PersonCompanyScopedFormMixin, ObjectPersonCompanyPermissionMixin, AuditFieldsMixin, UpdateView
):
    model = AbsenceRecord
    form_class = AbsenceRecordForm
    template_name = 'absence/absence_form.html'
    company_field_name = 'person__company'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Absence record updated.')
        return response


class DueToReturnListView(CompanyScopedQuerysetMixin, ListView):
    """Personnel due to return from Leave/TD/Course etc within the next N days."""

    model = AbsenceRecord
    template_name = 'absence/due_to_return_list.html'
    context_object_name = 'absence_list'
    paginate_by = 25
    company_field_name = 'person__company'

    def get_queryset(self):
        queryset = super().get_queryset().select_related('person', 'person__company')
        today = timezone.localdate()
        horizon_days = int(self.request.GET.get('days', 7))
        horizon = today + datetime.timedelta(days=horizon_days)
        return queryset.filter(
            to_date__gte=today, to_date__lte=horizon,
        ).exclude(status__in=[AbsenceRecord.STATUS_RETURNED, AbsenceRecord.STATUS_CANCELLED]).order_by('to_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['days'] = self.request.GET.get('days', '7')
        return context
