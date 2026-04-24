from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    es_comensal = models.BooleanField(default=False)
    es_hostelero = models.BooleanField(default=False)
    telefono = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.username