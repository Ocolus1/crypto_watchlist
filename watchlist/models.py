from django.db import models

class Wallet(models.Model):
    address = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.address