"""
Query-building helpers shared between each report's HTML view and its
CSV export view, so the two never drift out of sync.
"""

from absence.models import AbsenceRecord
from core.roles import accessible_company_ids
from dutyroster.models import DutyRoster
from personnel.models import Personnel
from strength.models import DailyStrength


def _scope_company(queryset, user, field='company_id__in'):
    company_ids = accessible_company_ids(user)
    if company_ids is not None:
        queryset = queryset.filter(**{field: company_ids})
    return queryset


def personnel_report_queryset(user, params):
    queryset = Personnel.objects.select_related('company', 'platoon', 'section', 'appointment')
    queryset = _scope_company(queryset, user)
    company = params.get('company', '').strip()
    status = params.get('status', '').strip()
    active = params.get('active', 'active').strip()
    if company:
        queryset = queryset.filter(company_id=company)
    if status:
        queryset = queryset.filter(status=status)
    if active == 'active':
        queryset = queryset.filter(is_active=True)
    elif active == 'inactive':
        queryset = queryset.filter(is_active=False)
    return queryset.order_by('company__name', 'rank', 'full_name')


def strength_report_queryset(user, params):
    queryset = DailyStrength.objects.select_related('company')
    queryset = _scope_company(queryset, user)
    company = params.get('company', '').strip()
    date_from = params.get('date_from', '').strip()
    date_to = params.get('date_to', '').strip()
    if company:
        queryset = queryset.filter(company_id=company)
    if date_from:
        queryset = queryset.filter(date__gte=date_from)
    if date_to:
        queryset = queryset.filter(date__lte=date_to)
    return queryset.order_by('-date', 'company__name')


def absence_report_queryset(user, params):
    queryset = AbsenceRecord.objects.select_related('person', 'person__company')
    queryset = _scope_company(queryset, user, field='person__company_id__in')
    company = params.get('company', '').strip()
    type_ = params.get('type', '').strip()
    status = params.get('status', '').strip()
    date_from = params.get('date_from', '').strip()
    date_to = params.get('date_to', '').strip()
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
    return queryset.order_by('-from_date')


def duty_report_queryset(user, params):
    queryset = DutyRoster.objects.select_related('company').prefetch_related('personnel_detailed')
    queryset = _scope_company(queryset, user)
    company = params.get('company', '').strip()
    duty_type = params.get('duty_type', '').strip()
    status = params.get('status', '').strip()
    date_from = params.get('date_from', '').strip()
    date_to = params.get('date_to', '').strip()
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
    return queryset.order_by('-duty_date').distinct()


def due_to_return_report_queryset(user, params, today, horizon_date):
    queryset = AbsenceRecord.objects.select_related('person', 'person__company')
    queryset = _scope_company(queryset, user, field='person__company_id__in')
    queryset = queryset.filter(to_date__gte=today, to_date__lte=horizon_date).exclude(
        status__in=[AbsenceRecord.STATUS_RETURNED, AbsenceRecord.STATUS_CANCELLED]
    )
    company = params.get('company', '').strip()
    if company:
        queryset = queryset.filter(person__company_id=company)
    return queryset.order_by('to_date')
