from django.db import models
from django.urls import reverse

from core.models import TimeStampedModel
from unitstructure.models import Company


class DailyStrength(TimeStampedModel):
    """
    Daily administrative strength return for a Company/sub-unit.
    One record per (date, company) - duplicate entry is prevented at
    the database and form level.
    """

    date = models.DateField()
    company = models.ForeignKey(Company, on_delete=models.PROTECT, related_name='daily_strengths')
    total_posted_strength = models.PositiveIntegerField(default=0)
    present = models.PositiveIntegerField(default=0)
    leave = models.PositiveIntegerField(default=0)
    temporary_duty = models.PositiveIntegerField('Temporary Duty', default=0)
    course = models.PositiveIntegerField(default=0)
    hospital_sick = models.PositiveIntegerField('Hospital / Sick', default=0)
    attached_out = models.PositiveIntegerField(default=0)
    other_absence = models.PositiveIntegerField(default=0)
    remarks = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Daily Strength Return'
        verbose_name_plural = 'Daily Strength Returns'
        ordering = ['-date', 'company__name']
        constraints = [
            models.UniqueConstraint(fields=['date', 'company'], name='unique_strength_per_company_per_day'),
        ]

    def __str__(self):
        return f"{self.company.name} - {self.date}"

    def get_absolute_url(self):
        return reverse('strength:detail', kwargs={'pk': self.pk})

    @property
    def total_absent(self):
        return self.leave + self.temporary_duty + self.course + self.hospital_sick + self.attached_out + self.other_absence

    @property
    def accounted_strength(self):
        return self.present + self.total_absent

    @property
    def is_balanced(self):
        return self.accounted_strength == self.total_posted_strength
