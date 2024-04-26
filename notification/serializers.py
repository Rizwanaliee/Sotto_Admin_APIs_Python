from rest_framework.serializers import ModelSerializer
from notification.models import Notifications

class NotificationSerializer(ModelSerializer):
    class Meta:
        model = Notifications
        fields = ['id', 'title','message','notificationType','isRead','createdAt','imageUrl']