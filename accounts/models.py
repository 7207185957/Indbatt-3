from django.contrib.auth.models import AbstractUser
from django.db import models

from core.roles import ROLE_CHOICES, VIEWER


class User(AbstractUser):
    """
    Custom user model so that every login is an individually attributable,
    named account (no shared/common logins) with an explicit role and,
    for Company Clerks, an assigned Company/sub-unit.
    """

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=VIEWER,
        help_text='Controls what this user can see and edit in the system.',
    )
    company = models.ForeignKey(
        'unitstructure.Company',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        help_text='Required for Company Clerk role. Restricts data access to this company/sub-unit.',
    )
    rank = models.CharField(max_length=50, blank=True, help_text='Rank of the account holder (for audit display only).')
    service_number = models.CharField(max_length=30, blank=True, help_text='Army/Service number of the account holder.')
    contact_number = models.CharField(max_length=20, blank=True)
    appointment = models.CharField(max_length=100, blank=True, help_text='Current appointment, e.g. Adjutant or Company Commander.')
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)

    class Meta:
        ordering = ['username']

    def __str__(self):
        full = self.get_full_name()
        return f"{self.username} ({full})" if full else self.username

    def display_role(self):
        return self.get_role_display()
