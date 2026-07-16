from django.db import models
from django.urls import reverse

from core.models import TimeStampedModel
from personnel.models import Personnel


class AbsenceRecord(TimeStampedModel):
    """
    Leave / Temporary Duty / Course / Hospital / Attachment / Other
    absence record for a person. Only non-sensitive, admin-approved
    destination text should be recorded (e.g. "Home Town", "Command
    Hospital", "Leave Station") - never operational deployment detail.
    """

    TYPE_LEAVE = 'LEAVE'
    TYPE_TD = 'TD'
    TYPE_COURSE = 'COURSE'
    TYPE_HOSPITAL = 'HOSPITAL'
    TYPE_ATTACHMENT = 'ATTACHMENT'
    TYPE_OTHER = 'OTHER'

    TYPE_CHOICES = (
        (TYPE_LEAVE, 'Leave'),
        (TYPE_TD, 'Temporary Duty'),
        (TYPE_COURSE, 'Course'),
        (TYPE_HOSPITAL, 'Hospital / Sick'),
        (TYPE_ATTACHMENT, 'Attachment'),
        (TYPE_OTHER, 'Other'),
    )

    STATUS_PLANNED = 'PLANNED'
    STATUS_ONGOING = 'ONGOING'
    STATUS_RETURNED = 'RETURNED'
    STATUS_CANCELLED = 'CANCELLED'

    STATUS_CHOICES = (
        (STATUS_PLANNED, 'Planned'),
        (STATUS_ONGOING, 'Ongoing'),
        (STATUS_RETURNED, 'Returned'),
        (STATUS_CANCELLED, 'Cancelled'),
    )

    person = models.ForeignKey(Personnel, on_delete=models.CASCADE, related_name='absence_records')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    from_date = models.DateField()
    to_date = models.DateField()
    authority_reference = models.CharField(
        'Authority / Reference', max_length=200,
        help_text='e.g. sanction letter number, competent authority approving the absence.',
    )
    destination = models.CharField(
        'Destination / Place', max_length=150, blank=True,
        help_text='Non-sensitive administrative reference only (e.g. Home Town, Command Hospital). '
                   'Do NOT enter operational locations.',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PLANNED)
    remarks = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Leave / TD / Absence Record'
        verbose_name_plural = 'Leave / TD / Absence Records'
        ordering = ['-from_date']

    def __str__(self):
        return f"{self.person.full_name} - {self.get_type_display()} ({self.from_date} to {self.to_date})"

    def get_absolute_url(self):
        return reverse('absence:detail', kwargs={'pk': self.pk})

    def status_badge_class(self):
        return {
            self.STATUS_PLANNED: 'info',
            self.STATUS_ONGOING: 'warning',
            self.STATUS_RETURNED: 'success',
            self.STATUS_CANCELLED: 'secondary',
        }.get(self.status, 'secondary')
