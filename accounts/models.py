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
   