"""
Role definitions shared across the Unit Administration System.

Keeping the role constants in one place (rather than duplicating strings
across apps) makes the role-based access control (RBAC) rules easy to
audit and change.
"""

SUPER_ADMIN = 'SUPER_ADMIN'
ADMIN_ADJT = 'ADMIN_ADJT'
CLERK = 'CLERK'
VIEWER = 'VIEWER'

ROLE_CHOICES = (
    (SUPER_ADMIN, 'Super Admin'),
    (ADMIN_ADJT, 'Adjt / Admin Branch'),
    (CLERK, 'Company Clerk'),
    (VIEWER, 'Viewer'),
)

# Roles that may create/edit/delete records (subject to company scoping
# for CLERK, enforced separately in mixins/querysets).
EDITOR_ROLES = (SUPER_ADMIN, ADMIN_ADJT, CLERK)

# Roles that have unrestricted (whole-unit) visibility.
FULL_VISIBILITY_ROLES = (SUPER_ADMIN, ADMIN_ADJT, VIEWER)


def is_super_admin(user):
    return user.is_authenticated and (user.is_superuser or user.role == SUPER_ADMIN)


def is_admin_adjt(user):
    return user.is_authenticated and user.role == ADMIN_ADJT


def is_clerk(user):
    return user.is_authenticated and user.role == CLERK


def is_viewer(user):
    return user.is_authenticated and user.role == VIEWER


def can_edit_records(user):
    """Whether the user's role permits add/edit actions anywhere in the app."""
    return user.is_authenticated and (user.is_superuser or user.role in EDITOR_ROLES)


def has_full_visibility(user):
    """Whether the user can see data for every company/sub-unit."""
    return user.is_authenticated and (user.is_superuser or user.role in FULL_VISIBILITY_ROLES)


def accessible_company_ids(user):
    """
    Return None if the user can see all companies, otherwise a list of
    company primary keys the user is restricted to (Company Clerk).
    """
    if has_full_visibility(user):
        return None
    if is_clerk(user):
        return [user.company_id] if user.company_id else []
    return []
