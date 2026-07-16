from django.db import models

from core.models import TimeStampedModel


class Company(TimeStampedModel):
    """A Company / sub-unit of the battalion (e.g. HQ Coy, A Coy, Support Coy)."""

    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True, help_text='Short code, e.g. HQ, A, B, C, D, SP')
    is_active = models.BooleanField(default=True)
    remarks = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = 'Company / Sub-unit'
        verbose_name_plural = 'Companies / Sub-units'
        ordering = ['name']

    def __str__(self):
        return self.name


class Platoon(TimeStampedModel):
    """A Platoon within a Company."""

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='platoons')
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    remarks = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = 'Platoon'
        verbose_name_plural = 'Platoons'
        unique_together = ('company', 'name')
        ordering = ['company__name', 'name']

    def __str__(self):
        return f"{self.name} ({self.company.code})"


class Section(TimeStampedModel):
    """A Section within a Platoon."""

    platoon = models.ForeignKey(Platoon, on_delete=models.CASCADE, related_name='sections')
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    remarks = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = 'Section'
        verbose_name_plural = 'Sections'
        unique_together = ('platoon', 'name')
        ordering = ['platoon__company__name', 'platoon__name', 'name']

    def __str__(self):
        return f"{self.name} ({self.platoon})"


class Appointment(TimeStampedModel):
    """An Appointment / Role / Trade held by personnel (e.g. Rifleman, Nb Sub Maj, Clerk, Driver)."""

    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Appointment / Trade'
        verbose_name_plural = 'Appointments / Trades'
        ordering = ['name']

    def __str__(self):
        return self.name
