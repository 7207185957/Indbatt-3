from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    """
    Abstract base class adding audit-friendly created/updated tracking to
    any model that inherits from it. `created_by`/`updated_by` are set by
    the views (see core.mixins.AuditFieldsMixin), not automatically,
    because only the view layer has access to the current request user.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        editable=False,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        editable=False,
    )

    class Meta:
        abstract = True
