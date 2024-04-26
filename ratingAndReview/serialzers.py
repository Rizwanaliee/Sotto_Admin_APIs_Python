from rest_framework.serializers import ModelSerializer, Serializer, ReadOnlyField,SerializerMethodField

from auth_APIs.models import ProviderUserAdditionalData
from .models import FavouriteProvider, RatingAndReview
from auth_APIs.serializers import ProfileDetailSerializer
from rest_framework import serializers

class FavouriteProviderSerializer(ModelSerializer):
    providerId = ProfileDetailSerializer()
    additionalData=SerializerMethodField()
    class Meta:
        model = FavouriteProvider
        fields = ['id', 'providerId', 'createdAt', 'additionalData']
    def get_additionalData(self,obj):
        add = ProviderUserAdditionalData.objects.filter(userId=obj.providerId.id).first()
        addi = {
            "fee":add.fee,
            "experience":add.experience
        }
        return addi

        

class RatingAndReviewSerializer(ModelSerializer):
    class Meta:
        model = RatingAndReview
        fields = ['id', 'providerId', 'userId','providerRating', 'feedbackComment','consultationId']
    

    def create(self, validated_data):
        if "feedbackComment" in validated_data:
            feedbackComment = validated_data['feedbackComment']
        else:
            feedbackComment = None
        rating = RatingAndReview.objects.create(
            providerId = validated_data["providerId"],
            userId = validated_data["userId"],
            providerRating = validated_data["providerRating"],
            feedbackComment = feedbackComment,
            consultationId = validated_data["consultationId"]
        )
        return rating


class RatingAndReviewForDetailSerializer(ModelSerializer):
    providerId = ProfileDetailSerializer()

    class Meta:
        model = RatingAndReview
        fields = ['id','providerRating', 'feedbackComment','providerId']

class RatingAndReviewForDetailSerializer2(ModelSerializer):
    userId = ProfileDetailSerializer()

    class Meta:
        model = RatingAndReview
        fields = ['id','providerRating', 'feedbackComment','userId', 'createdAt']

# class RatingAndReviewForDetailSerializer3(Serializer):
#     userId = ProfileDetailSerializer()
#     id=serializers.IntegerField()
#     providerRating=serializers.IntegerField()
#     feedbackComment=serializers.CharField()
#     createdAt=serializers.DateTimeField()