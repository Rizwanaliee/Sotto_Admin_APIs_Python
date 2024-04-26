from pyexpat import model
from django.db import models

# Create your models here.
class DefaultPriceAndFeeSetting(models.Model):
    fee = models.IntegerField(null=False, default=0, blank=True)
    minPrice = models.IntegerField(null=False, default=0, blank=True)
    maxPrice = models.IntegerField(null=False, default=0, blank=True)

    class Meta:
        db_table = 'default_settings'