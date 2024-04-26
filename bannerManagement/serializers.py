from rest_framework.serializers import ModelSerializer
from .models import Banner

class BannerListSerializer(ModelSerializer):
    class Meta:
        model = Banner
        fields = ['id', 'title', 'imageUrl', 'createdAt']