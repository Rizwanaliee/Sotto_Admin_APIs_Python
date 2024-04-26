from django.db import models
from auth_APIs.models import User
from django.utils.timezone import now

# Create your models here.


class Notifications(models.Model):
    notification_for = ((1, "admin"), (2, "patient"), (3, "provider"))
    notficationStatus = ((1,"pushNotificaion"),(2,"callNotification"))
    title = models.CharField(max_length=255)
    message = models.CharField(max_length=255, null=True, default=None)
    imageUrl = models.CharField(max_length=255, null=True, default=None)
    userId = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='userId_Notofications', db_column='userId')
    notificationFor = models.IntegerField(
        choices=notification_for, null=False, default=1)
    notificationType = models.IntegerField(
        choices=notficationStatus, null=False, default=1)
    isRead = models.BooleanField(default=False, null=False)
    createdAt = models.DateTimeField(default=now, editable=False)
    updatedAt = models.DateTimeField(default=now, editable=False)

    class Meta:
        db_table = 'notifications'
