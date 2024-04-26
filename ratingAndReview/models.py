from django.db import models
from auth_APIs.models import User
from django.utils.timezone import now

from searchAPIs.models import Consultantion

# Create your models here.


class FavouriteProvider(models.Model):
    userId = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column="userId",
        related_name="favourite_from_userId",
    )
    providerId = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column="providerId",
        related_name="favourite_to_providerId",
        null=True
    )
    createdAt = models.DateTimeField(default=now, editable=False)

    class Meta:
        db_table = 'favourite_providers'


class RatingAndReview(models.Model):
    userId = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column="userId",
        related_name="rating_from_userId",
    )
    providerId = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column="providerId",
        related_name="rating_to_providerId",
        null=True
    )
    consultationId = models.OneToOneField(
        Consultantion,
        on_delete=models.CASCADE,
        db_column="consultationId",
        related_name="rating_to_consultationId",
        null=True,
        unique=True
    )
    providerRating = models.IntegerField(null=True, blank=True)
    feedbackComment = models.CharField(max_length=255, null=True, blank=True)
    createdAt = models.DateTimeField(default=now, editable=False)
    class Meta:
        db_table = 'rating_review_providers'
