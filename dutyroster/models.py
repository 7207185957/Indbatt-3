from django.db import models
from django.urls import reverse

from core.models import TimeStampedModel
from personnel.models import Personnel
from unitstructure.models import Company


class DutyRoster(TimeStampedModel):
    """
    Administrative duty roster entry (e.g. Quarter Guard, Orderly Officer,
    Fire Picket, Fatigue). Location/post must be recorded only as generic
    administrative text - never operationally sensitive tasking detail.
    """

    STATUS_SCHEDULED = 'SCHEDULED'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_CANCELLED = 'CANCELLED'

    STATUS_CHOICES = (
        (STATUS_SCHEDULED, 'Scheduled'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    )

    duty_date = models.DateField()
    duty_type = models.CharField(
        max_length=100,
        help_text='e.g. Quarter Guard, Orderly Officer/NCO, Fire Picket, Fatigue, Kitchen Duty.',
    )
    company = models.ForeignKey(Company, on_delete=models.PROTECT, related_name='duty_rosters')
    personnel_detailed = models.ManyToManyField(Personnel, related_name='duty_assignments', blank=False)
    duty_location = models.CharField(
        'Duty Location / Post', max_length=150,
        help_text='Generic administrative description only (e.g. "Unit Lines", "Quarter Guard"). '
                   'Do NOT enter operational deployment locations.',
    )
    shift_time = models.CharField('Shift / Time', max_length=100, help_text='e.g. 0600-1400 hrs')
    remarks = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SCHEDULED)

    class Meta:
        verbose_name = 'Duty Roster Entry'
        verbose_name_plural = 'Duty Roster Entries'
        ordering = ['-duty_date', 'company__name']

    def __str__(self):
        return f"{self.duty_type} - {self.duty_date} ({self.company.code})"

    def get_absolute_url(self):
        return reverse('dutyroster:detail', kwargs={'pk': self.pk})

    def status_badge_class(self):
        return {
            self.STATUS_SCHEDULED: 'info',
            self.STATUS_COMPLETED: 'success',
            self.STATUS_CANCELLED: 'secondary',
        }.get(self.status, 'secondary')
