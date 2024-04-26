from rest_framework.serializers import ModelSerializer,ReturnDict
from .models import RequestAssign, Consultantion
from auth_APIs.models import User,ProviderUserAdditionalData, licenseType
from searchAPIs.models import Consultantion


class ProviderDetailSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'firstName', 'lastName','fullName', 'email',
                  'mobileNo', 'profileImage','zipCode','genderType','state']
    
class ConsultationDetailSerializer(ModelSerializer):
    userId = ProviderDetailSerializer()
    class Meta:
        model = Consultantion
        fields = ['id','userId','createdAt','consultantionStatus','paymentStatus','callDuration']

class RequestAssignSerializer(ModelSerializer):
    consultantiontId = ConsultationDetailSerializer()
    class Meta:
        model = RequestAssign
        fields = ['id', 'assignStatus','consultantiontId']

class LisenceTypeDetails(ModelSerializer):
    class Meta:
        model = licenseType
        fields = ['therapyType']

class ProviderAdditionalDataSerializer2(ModelSerializer):
    userId=ProviderDetailSerializer()
    # licenseTypeId=LisenceTypeDetails()
    class Meta:
        model = ProviderUserAdditionalData
        fields = ['userId','experience','fee','about']
class ProviderAdditionalDataSerializer3(ModelSerializer):
    # licenseTypeId=LisenceTypeDetails()
    class Meta:
        model = ProviderUserAdditionalData
        fields = ['experience','fee','about']

class ConsultationDetailSessionHistorySerializer(ModelSerializer):
    providerId = ProviderDetailSerializer()
    class Meta:
        model = Consultantion
        fields = ['id','providerId','createdAt']

class ConsultationDetailSessionHistorProviderySerializer(ModelSerializer):
    userId = ProviderDetailSerializer()
    class Meta:
        model = Consultantion
        fields = ['id','userId','callDuration','consultantionStatus','paymentStatus','createdAt']

        

