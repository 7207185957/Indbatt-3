"""
Reusable class-based-view mixins implementing role-based access control
(RBAC) and audit-field tracking consistently across every module
(personnel, absence, strength, dutyroster, reports, accounts).
"""

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied

from core.roles import (
    accessible_company_ids,
    can_edit_records,
    has_full_visibility,
    is_clerk,
    is_super_admin,
)


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Restrict a view to a fixed list of roles (checked via `allowed_roles`)."""

    allowed_roles = ()
    raise_exception = True

    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        return user.role in self.allowed_roles


class EditRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Restrict create/update/delete views to roles that may edit records."""

    raise_exception = True

    def test_func(self):
        return can_edit_records(self.request.user)


class SuperAdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Restrict a view to Super Admin only (e.g. user account management)."""

    raise_exception = True

    def test_func(self):
        return is_super_admin(self.request.user)


class CompanyScopedQuerysetMixin:
    """
    Automatically scope a ListView/DetailView queryset to the logged-in
    user's company when the user is a Company Clerk. Super Admin,
    Adjt/Admin Branch and Viewer see every company.

    Views using this mixin must define `company_field_name` if the
    model's path to Company is not simply `company`.
    """

    company_field_name = 'company'

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        company_ids = accessible_company_ids(user)
        if company_ids is None:
            return queryset
        lookup = f"{self.company_field_name}_id__in"
        return queryset.filter(**{lookup: company_ids})


class CompanyScopedFormMixin:
    """
    For Create/Update views: restrict the `company` choice field to the
    Clerk's own company, and prevent a Clerk from saving a record for a
    different company by re-checking on form_valid.
    """

    company_field_name = 'company'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        if is_clerk(user) and self.company_field_name in form.fields:
            field = form.fields[self.company_field_name]
            if user.company_id:
                field.queryset = field.queryset.filter(pk=user.company_id)
                field.initial = user.company_id
            else:
                field.queryset = field.queryset.none()
        return form

    def form_valid(self, form):
        user = self.request.user
        if is_clerk(user):
            submitted_company = getattr(form.instance, f"{self.company_field_name}_id", None)
            if not user.company_id or submitted_company != user.company_id:
                raise PermissionDenied('Company Clerks may only manage records for their own company/sub-unit.')
        return super().form_valid(form)


class PersonCompanyScopedFormMixin:
    """
    Variant of CompanyScopedFormMixin for forms that reference a person
    (e.g. AbsenceRecord.person) rather than a direct `company` field.
    Restricts the person choice field to personnel of accessible
    companies, and re-validates on save.
    """

    person_field_name = 'person'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        company_ids = accessible_company_ids(self.request.user)
        if company_ids is not None and self.person_field_name in form.fields:
            field = form.fields[self.person_field_name]
            field.queryset = field.queryset.filter(company_id__in=company_ids)
        return form

    def form_valid(self, form):
        company_ids = accessible_company_ids(self.request.user)
        if company_ids is not None:
            person = getattr(form.instance, self.person_field_name)
            if person is None or person.company_id not in company_ids:
                raise PermissionDenied('Company Clerks may only manage records for personnel in their own company/sub-unit.')
        return super().form_valid(form)


class PersonnelDetailedScopedFormMixin:
    """
    Restrict the `personnel_detailed` M2M field (used by DutyRoster) to
    personnel belonging to companies the current user can access, so a
    Company Clerk cannot detail personnel from another company for duty.
    """

    personnel_field_name = 'personnel_detailed'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        company_ids = accessible_company_ids(self.request.user)
        if company_ids is not None and self.personnel_field_name in form.fields:
            field = form.fields[self.personnel_field_name]
            field.queryset = field.queryset.filter(company_id__in=company_ids)
        return form


class AuditFieldsMixin:
    """Stamp created_by/updated_by automatically on save, for audit trails."""

    def form_valid(self, form):
        if form.instance.pk is None:
            form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class ObjectCompanyPermissionMixin:
    """
    For DetailView/UpdateView/DeleteView: raise PermissionDenied if a
    Company Clerk tries to open a record that does not belong to their
    own company/sub-unit.
    """

    company_field_name = 'company'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user
        company_ids = accessible_company_ids(user)
        if company_ids is not None:
            obj_company_id = getattr(obj, f"{self.company_field_name}_id", None)
            if obj_company_id not in company_ids:
                raise PermissionDenied('You do not have access to this record.')
        return obj


class ObjectPersonCompanyPermissionMixin:
    """
    Variant of ObjectCompanyPermissionMixin for objects that reference a
    person (e.g. AbsenceRecord.person) rather than a direct company field.
    """

    person_field_name = 'person'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        company_ids = accessible_company_ids(self.request.user)
        if company_ids is not None:
            person = getattr(obj, self.person_field_name)
            if person is None or person.company_id not in company_ids:
                raise PermissionDenied('You do not have access to this record.')
        return obj


def user_can_see_full_unit(user):
    return has_full_visibility(user)
