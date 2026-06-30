from django.db import models
from django.conf import settings
from apps.masters.models import MasterProfile
from apps.services.models import ServiceCategory
# Create your models here.

class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        ACCEPTED = 'ACCEPTED', 'Accepted'
        ON_THE_WAY = 'ON_THE_WAY', 'On the way'
        IN_PROGRESS = 'IN_PROGRESS', 'In progress'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'
        REJECTED = 'REJECTED', 'Rejected'

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    master = models.ForeignKey(
        MasterProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )
    service_category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    problem_description = models.TextField()
    customer_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    customer_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    customer_address = models.TextField(blank=True)
    need_master_visit = models.BooleanField(default=False)
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING
    )
    offered_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    final_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.status}"


class CarProblemImage(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='problem_images/')
