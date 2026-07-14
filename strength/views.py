from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView, TemplateView, UpdateView

from core.mixins import (
    AuditFieldsMixin,
    CompanyScopedFormMixin,
    CompanyScopedQuerysetMixin,
    EditRequiredMixin,
    ObjectCompanyPermissionMixin,
)
from core.roles import accessible_company_ids
from unitstructure.models import Company

from .forms import DailyStrengthForm
from .models import DailyStrength


class DailyStrengthListView(CompanyScopedQuerysetMixin, ListView):
    model = DailyStrength
    template_name = 'strength/strength_list.html'
    context_object_name = 'strength_list'
    paginate_by = 25

    def get_queryset(self):
        queryset = super().get_queryset().select_related('company')
        company = self.request.GET.get('company', '').strip()
        date_from = self.request.GET.get('date_from', '').strip()
        date_to = self.request.GET.get('date_to', '').strip()
        if company:
            queryset = queryset.filter(company_id=company)
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        return queryset.order_by('-date', 'company__name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        company_ids = accessible_company_ids(user)
        companies = Company.objects.filter(is_active=True)
        if company_ids is not None:
            companies = companies.filter(pk__in=company_ids)
        context['companies'] = companies
        context['selected_company'] = self.request.GET.get('company', '')
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')
        return context


class DailyStrengthDetailView(CompanyScopedQuerysetMixin, ObjectCompanyPermissionMixin, DetailView):
    model = DailyStrength
    template_name = 'strength/strength_detail.html'
    context_object_name = 'strength'


class DailyStrengthCreateView(EditRequiredMixin, CompanyScopedFormMixin, AuditFieldsMixin, CreateView):
    model = DailyStrength
    form_class = DailyStrengthForm
    template_name = 'strength/strength_form.html'

    def get_initial(self):
        initial = super().get_initial()
        initial['date'] = timezone.localdate()
        return initial

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Daily strength entry saved.')
        return response


class DailyStrengthUpdateView(
    EditRequiredMixin, CompanyScopedFormMixin, ObjectCompanyPermissionMixin, AuditFieldsMixin, UpdateView
):
    model = DailyStrength
    form_class = DailyStrengthForm
    template_name = 'strength/strength_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Daily strength entry updated.')
        return response


class StrengthSummaryView(TemplateView):
    """Company-wise summary of strength for a single selected date."""

    template_name = 'strength/strength_summary.html'

    def get_queryset(self):
        return DailyStrength.objects.select_related('company')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        date_str = self.request.GET.get('date', '')
        selected_date = timezone.localdate()
        if date_str:
            try:
                selected_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        entries = self.get_queryset().filter(date=selected_date)
        user = self.request.user
        company_ids = accessible_company_ids(user)
        if company_ids is not None:
            entries = entries.filter(company_id__in=company_ids)

        totals = entries.aggregate(
            total_posted=Sum('total_posted_strength'),
            total_present=Sum('present'),
            total_leave=Sum('leave'),
            total_td=Sum('temporary_duty'),
            total_course=Sum('course'),
            total_hospital=Sum('hospital_sick'),
            total_attached_out=Sum('attached_out'),
            total_other=Sum('other_absence'),
        )

        companies = Company.objects.filter(is_active=True)
        if company_ids is not None:
            companies = companies.filter(pk__in=company_ids)
        reported_company_ids = set(entries.values_list('company_id', flat=True))
        missing_companies = companies.exclude(pk__in=reported_company_ids)

        context['selected_date'] = selected_date
        context['entries'] = entries.order_by('company__name')
        context['totals'] = totals
        context['missing_companies'] = missing_companies
        return context
