from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    litres_per_day = models.CharField(max_length=20)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.name
