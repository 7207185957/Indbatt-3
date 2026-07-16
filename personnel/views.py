from django.contrib import messages
from django.db.models import Q
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from core.mixins import (
    AuditFieldsMixin,
    CompanyScopedFormMixin,
    CompanyScopedQuerysetMixin,
    EditRequiredMixin,
    ObjectCompanyPermissionMixin,
)
from core.roles import accessible_company_ids
from unitstructure.models import Company

from .forms import PersonnelForm
from .models import Personnel


class PersonnelListView(CompanyScopedQuerysetMixin, ListView):
    model = Personnel
    template_name = 'personnel/personnel_list.html'
    context_object_name = 'personnel_list'
    paginate_by = 25

    def get_queryset(self):
        queryset = super().get_queryset().select_related('company', 'platoon', 'section', 'appointment')
        q = self.request.GET.get('q', '').strip()
        company = self.request.GET.get('company', '').strip()
        status = self.request.GET.get('status', '').strip()
        active = self.request.GET.get('active', '').strip()

        if q:
            queryset = queryset.filter(
                Q(army_number__icontains=q) | Q(full_name__icontains=q) | Q(rank__icontains=q)
            )
        if company:
            queryset = queryset.filter(company_id=company)
        if status:
            queryset = queryset.filter(status=status)
        if active == 'active':
            queryset = queryset.filter(is_active=True)
        elif active == 'inactive':
            queryset = queryset.filter(is_active=False)
        else:
            queryset = queryset.filter(is_active=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        company_ids = accessible_company_ids(user)
        companies = Company.objects.filter(is_active=True)
        if company_ids is not None:
            companies = companies.filter(pk__in=company_ids)
        context['companies'] = companies
        context['status_choices'] = Personnel.STATUS_CHOICES
        context['q'] = self.request.GET.get('q', '')
        context['selected_company'] = self.request.GET.get('company', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_active'] = self.request.GET.get('active', 'active')
        return context


class PersonnelDetailView(CompanyScopedQuerysetMixin, ObjectCompanyPermissionMixin, DetailView):
    model = Personnel
    template_name = 'personnel/personnel_detail.html'
    context_object_name = 'person'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['absence_records'] = self.object.absence_records.order_by('-from_date')[:10]
        context['duty_records'] = self.object.duty_assignments.order_by('-duty_date')[:10]
        return context


class PersonnelCreateView(EditRequiredMixin, CompanyScopedFormMixin, AuditFieldsMixin, CreateView):
    model = Personnel
    form_class = PersonnelForm
    template_name = 'personnel/personnel_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Personnel record for {self.object.full_name} created.")
        return response


class PersonnelUpdateView(
    EditRequiredMixin, CompanyScopedFormMixin, ObjectCompanyPermissionMixin, AuditFieldsMixin, UpdateView
):
    model = Personnel
    form_class = PersonnelForm
    template_name = 'personnel/personnel_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Personnel record for {self.object.full_name} updated.")
        return response
