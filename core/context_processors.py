from django.conf import settings

from core.roles import can_edit_records, is_super_admin


def unit_branding(request):
    """Make unit name and RBAC flags available to every template."""
    user = getattr(request, 'user', None)
    return {
        'UNIT_NAME': getattr(settings, 'UNIT_NAME', 'Unit Administration System'),
        'can_edit': bool(user and user.is_authenticated and can_edit_records(user)),
        'is_super_admin_user': bool(user and user.is_authenticated and is_super_admin(user)),
    }
