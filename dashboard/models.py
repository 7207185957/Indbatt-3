from django.db import models


class DashboardAnnouncement(models.Model):
    PRIORITY_INFO = 'INFO'
    PRIORITY_IMPORTANT = 'IMPORTANT'
    PRIORITY_URGENT = 'URGENT'
    PRIORITY_CHOICES = [
        (PRIORITY_INFO, 'Information'),
        (PRIORITY_IMPORTANT, 'Important'),
        (PRIORITY_URGENT, 'Urgent'),
    ]

    message = models.CharField(max_length=300)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default=PRIORITY_INFO)
    is_active = models.BooleanField(default=True)
    starts_on = models.DateField(blank=True, null=True)
    ends_on = models.DateField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', '-id']

    def __str__(self):
        return self.message


class DashboardHeroSlide(models.Model):
    title = models.CharField(max_length=120)
    subtitle = models.CharField(max_length=250, blank=True)
    image = models.ImageField(upload_to='dashboard_slides/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.title


class UnitEvent(models.Model):
    EVENT = 'EVENT'
    BIRTHDAY = 'BIRTHDAY'
    REMINDER = 'REMINDER'
    TYPE_CHOICES = [
        (EVENT, 'Event'),
        (BIRTHDAY, 'Birthday'),
        (REMINDER, 'Reminder'),
    ]

    title = models.CharField(max_length=150)
    event_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=EVENT)
    event_date = models.DateField()
    description = models.TextField(blank=True)
    company = models.ForeignKey('unitstructure.Company', on_delete=models.SET_NULL, null=True, blank=True, related_name='dashboard_events')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['event_date', 'title']

    def __str__(self):
        return f'{self.title} - {self.event_date}'
