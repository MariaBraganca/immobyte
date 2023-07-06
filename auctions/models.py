from django.db import models

# Create your models here.
class Auction(models.Model):
    number = models.CharField(max_length=20)
    court = models.CharField(max_length=200)
    object = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    appointment = models.DateTimeField()
    description = models.TextField()
    report_url = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
