from django.db import models
from django.conf import settings
from django.db import models
from apps.masters.models import MasterProfile
from apps.orders.models import Order
# Create your models here.

class Review(models.Model):
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    master = models.ForeignKey(
        MasterProfile,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='review'
    )
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.master.full_name} - {self.rating}"
