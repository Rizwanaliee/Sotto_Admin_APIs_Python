from django.db import models
from django.utils.timezone import now
from auth_APIs.models import User
from searchAPIs.models import Consultantion

# Create your models here.

class SavedCardDetail(models.Model):
    cardStatusVal = ((1, "ordinary"), (2, "default"))
    userId = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='customerCard', db_column='userId')
    paymentMethodId = models.CharField(max_length=255, null=False, blank=False)
    fingerprint = models.CharField(max_length=255, null=False, blank=False)
    cardStatus = models.IntegerField(choices=cardStatusVal, null=False, default=1)
    createdAt = models.DateTimeField(default=now, editable=False)
    class Meta:
        db_table = 'CardDetails'


class Transaction(models.Model):
    paymentStatuses = ((1, "initiated"), (2, "success"), (3, "pending"),
                       (4, "Falied"), (5, "refunded"), (6, "failed"), (7, "cancelled"))
    paymentId = models.CharField(
        max_length=255, default=None, null=False, blank=False)
    consultantiontId = models.ForeignKey(
        Consultantion, on_delete=models.CASCADE, related_name='consultantiont_trans_Id', db_column='consultantiontId', null=False)
    userId = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='userId_transaction', db_column='userId')
    amount = models.DecimalField(
        max_length=255, default=0.00, decimal_places=2, max_digits=10, null=False
    )
    paymentMethodId = models.ForeignKey(
        SavedCardDetail,on_delete=models.SET_NULL,related_name='payment_method_ref', db_column='paymentMethodId', null=True)
    paymentStatus = models.IntegerField(choices=paymentStatuses, default=1)
    callDuration = models.IntegerField(default=None, null=False)
    reciept = models.CharField(
        max_length=255, default=None, null=True, blank=True)
    stripeFee = models.DecimalField(
        max_length=255, default=0.00, decimal_places=2, max_digits=10, null=True
    )
    netAmmount = models.DecimalField(
        max_length=255, default=0.00, decimal_places=2, max_digits=10, null=True
    )
    adminCharge = models.DecimalField(
        max_length=255, default=0.00, decimal_places=2, max_digits=10, null=True
    )
    
    createdAt = models.DateTimeField(default=now, editable=False)
    updatedAt = models.DateTimeField(default=now, editable=False)

    class Meta:
        db_table = 'transactions'
