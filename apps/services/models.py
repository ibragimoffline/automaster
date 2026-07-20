from django.db import models
from django.db import models
from apps.masters.models import MasterProfile

class ServiceCategory(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class MasterService(models.Model):
    master = models.ForeignKey(
        MasterProfile,
        on_delete=models.CASCADE,
        related_name='services'
    )
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.CASCADE,
        related_name='master_services'
    )
    title = models.CharField(max_length=255)
    price_from = models.DecimalField(max_digits=12, decimal_places=2)
    price_to = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.master.full_name} - {self.title}"
