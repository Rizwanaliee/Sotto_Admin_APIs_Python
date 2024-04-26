from django.db import models
from django.utils.timezone import now

# Create your models here.
class Banner(models.Model):
    title = models.CharField(max_length=250, null=False)
    imageUrl = models.CharField(max_length=250, null=False)
    createdAt = models.DateTimeField(default=now, editable=False)
    updatedAt = models.DateTimeField(default=now, editable=False)

    class Meta:
        db_table = 'banners'