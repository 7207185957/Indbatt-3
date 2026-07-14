from django.db import models
from django.urls import reverse

from core.models import TimeStampedModel
from unitstructure.models import Appointment, Company, Platoon, Section


class Personnel(TimeStampedModel):
    """
    Personnel master record. Deliberately holds only non-classified,
    non-operational administrative data (identity, unit posting, and
    administrative status) - no operational deployment, tasking, or
    location-sensitive information should ever be entered here.
    """

    STATUS_PRESENT = 'PRESENT'
    STATUS_LEAVE = 'LEAVE'
    STATUS_TD = 'TD'
    STATUS_COURSE = 'COURSE'
    STATUS_HOSPITAL = 'HOSPITAL'
    STATUS_ATTACHED_OUT = 'ATTACHED_OUT'
    STATUS_OTHER = 'OTHER'

    STATUS_CHOICES = (
        (STATUS_PRESENT, 'Present'),
        (STATUS_LEAVE, 'Leave'),
        (STATUS_TD, 'Temporary Duty'),
        (STATUS_COURSE, 'Course'),
        (STATUS_HOSPITAL, 'Hospital / Sick'),
        (STATUS_ATTACHED_OUT, 'Attached Out'),
        (STATUS_OTHER, 'Other'),
    )

    army_number = models.CharField(
        'Army / Service Number', max_length=30, unique=True, db_index=True,
    )
    rank = models.CharField(max_length=50)
    full_name = models.CharField(max_length=150)
    company = models.ForeignKey(Company, on_delete=models.PROTECT, related_name='personnel')
    platoon = models.ForeignKey(
        Platoon, on_delete=models.SET_NULL, null=True, blank=True, related_name='personnel',
    )
    section = models.ForeignKey(
        Section, on_delete=models.SET_NULL, null=True, blank=True, related_name='personnel',
    )
    appointment = models.ForeignKey(
        Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name='personnel',
        verbose_name='Appointment / Trade',
    )
    date_of_joining_unit = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PRESENT)
    remarks = models.TextField(blank=True)
    is_active = models.BooleanField(
        default=True,
        help_text='Untick when a person permanently leaves the unit (posted out / discharged / retired).',
    )

    class Meta:
        verbose_name = 'Personnel'
        verbose_name_plural = 'Personnel'
        ordering = ['company__name', 'rank', 'full_name']

    def __str__(self):
        return f"{self.army_number} - {self.rank} {self.full_name}"

    def get_absolute_url(self):
        return reverse('personnel:detail', kwargs={'pk': self.pk})

    def status_badge_class(self):
        return {
            self.STATUS_PRESENT: 'success',
            self.STATUS_LEAVE: 'warning',
            self.STATUS_TD: 'info',
            self.STATUS_COURSE: 'info',
            self.STATUS_HOSPITAL: 'danger',
            self.STATUS_ATTACHED_OUT: 'secondary',
            self.STATUS_OTHER: 'secondary',
        }.get(self.status, 'secondary')
