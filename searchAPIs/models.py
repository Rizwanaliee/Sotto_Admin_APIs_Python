from django.db import models
from auth_APIs.models import User
from django.utils.timezone import now
# Create your models here.

class Consultantion(models.Model):
    paymentMode = ((1, "online"), (2, "cash"))
    paymentStatus = (
        (1, "pending"),
        (2, "payment_recieved"),
        (3, "payment_cancelled"),
        (4, "refunded"),
    )
    consultantionStatus = (
        (1, "pending"),
        (2, "accepted"),
        (3, "rejected"),
        (4, "completed"),
        (5, "failed"),
        (6,"cancelled")
    )
    userId = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column="userId",
        related_name="consultantion_userId",
    )
    providerId = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column="providerId",
        related_name="consultantion_doctorId",
        null=True
    )
    paymentMode = models.IntegerField(choices=paymentMode, null=True)
    paymentStatus = models.IntegerField(choices=paymentStatus, null=True)
    consultantionStatus = models.IntegerField(
        choices=consultantionStatus, null=False)
    consultantiontFee = models.DecimalField(
        max_length=255, default=0.00, decimal_places=2, max_digits=10, null=True
    )
    callDuration = models.IntegerField(default=None, null=True)
    createdAt = models.DateTimeField(default=now, editable=False)
    updatedAt = models.DateTimeField(default=now, editable=False)
    doctorRating = models.IntegerField(null=True)
    feedback = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = 'consultantions'

class RequestAssign(models.Model):
    assignStatus = models.IntegerField(
        choices=((1, "Pending"), (2, "Accepted"), (3, "Rejected"), (4, "completed"),(5, "failed"),(6,"cancelled"),(7,"declined")), default=1)
    consultantiontId = models.ForeignKey(
        Consultantion, on_delete=models.CASCADE, related_name='consultantiont_assign_Id', db_column='consultantiontId', null=False)
    providerId = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column="providerId",
        related_name="provider_assign_id",
        null=False
    )
    createdAt = models.DateTimeField(default=now, editable=False)
    class Meta:
        db_table = 'requests_assign'


class ProviderProgressNote(models.Model):
    consultantiontId = models.ForeignKey(
        Consultantion, on_delete=models.CASCADE, related_name='consultantiont_for_note', db_column='consultantiontId', null=False)
    treatmentGoal = models.CharField(max_length=450, null=False)
    subjective = models.CharField(max_length=450, null=False)
    objective = models.CharField(max_length=450, null=False)
    assessment = models.CharField(max_length=450, null=False)
    plan = models.CharField(max_length=450, null=False)
    signatureUrl = models.CharField(max_length=255, null=False)
    createdAt = models.DateTimeField(default=now, editable=False)
    class Meta:
        db_table = 'provider_progress_notes'
