from django.db import models
from django.conf import settings

class MasterProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='master_profile'
    )
    full_name = models.CharField(max_length=255)
    experience_years = models.PositiveIntegerField(default=0)
    bio = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    can_visit_customer = models.BooleanField(default=False)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.full_name


class Workshop(models.Model):
    master = models.OneToOneField(
        MasterProfile,
        on_delete=models.CASCADE,
        related_name='workshop'
    )
    name = models.CharField(max_length=255)
    region = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    open_time = models.TimeField(null=True, blank=True)
    close_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return self.name
