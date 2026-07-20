from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Role(models.TextChoices):
        CUSTOMER = 'CUSTOMER', 'Customer'
        MASTER = 'MASTER', 'Master'
        ADMIN = 'ADMIN', 'Admin'

    phone = models.CharField(max_length=20, unique=True)
    phone_verified = models.BooleanField(default=False)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER
    )

    def __str__(self):
        return f"{self.username} - {self.role}"
