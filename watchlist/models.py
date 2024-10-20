from django.db import models

class Wallet(models.Model):
    address = models.CharField(max_length=100, unique=True)
    tag = models.CharField(max_length=100, default="Store")
    date_added = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return self.address