from rest_framework.serializers import ModelSerializer, SerializerMethodField

from ratingAndReview.models import RatingAndReview
from .models import User, licenseType, ProviderUserLicenseDocs, ProviderUserAdditionalData,PatientUserAdditionalData
from django.contrib.auth.hashers import make_password
from django.db.models import Avg


class UserRegistrationSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'firstName', 'lastName', 'fullName', 'password', 'email',
                  'mobileNo', 'profileImage', 'deviceType', 'userType', 'genderType', 'lat', 'lng', 'zipCode', 'countryCode', 'dateOfBirth','state','stripeCustomerId']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        if "deviceToken" in validated_data:
            deviceToken = validated_data['deviceToken']
        else:
            deviceToken = None
        if "mobileNo" in validated_data:
            mobileNo = validated_data['mobileNo']
        else:
            mobileNo = None

        if "genderType" in validated_data:
            genderType = validated_data['genderType']
        else:
            genderType = None

        if "lat" in validated_data:
            lat = validated_data['lat']
        else:
            lat = None

        if "lng" in validated_data:
            lng = validated_data['lng']
        else:
            lng = None
        if "dateOfBirth" in validated_data:
            dateOfBirth = validated_data['dateOfBirth']
        else:
            dateOfBirth = None
        if 'countryCode' in validated_data:
            countryCode = validated_data['countryCode']
        else:
            countryCode = None
        # if 'stripeCustomerId' in validated_data:
        #     stripeCustomerId = validated_data['stripeCustomerId']
        # else:
        #     stripeCustomerId = None
        user = User.objects.create(
            firstName=validated_data['firstName'],
            lastName=validated_data['lastName'],
            fullName=validated_data["fullName"],
            email=validated_data['email'],
            password=make_password(validated_data['password']),
            mobileNo=mobileNo,
            deviceType=validated_data['deviceType'],
            userType=validated_data['userType'],
            genderType=genderType,
            lat=lat,
            lng=lng,
            zipCode=validated_data["zipCode"],
            dateOfBirth=dateOfBirth,
            countryCode=countryCode,
            state=validated_data['state'],
            stripeCustomerId = validated_data['stripeCustomerId']
        )
        return user


class LicenseTypeSerializer(ModelSerializer):
    class Meta:
        model = licenseType
        fields = ['id', 'licenseTypeName']


class ProfileDetailSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'firstName', 'lastName','fullName', 'email',
                  'mobileNo', 'profileImage', 'userType', 'genderType', 'zipCode', 'dateOfBirth','state']


class LisenceDocsSerializer(ModelSerializer):
    class Meta:
        model = ProviderUserLicenseDocs
        fields = ['id', 'providerUserDocUrl']


class ProviderAdditionalDataSerializer(ModelSerializer):
    class Meta:
        model = ProviderUserAdditionalData
        fields = ['experience', 'about']

class PatientAdditionalDataSerializer(ModelSerializer):
    class Meta:
        model = PatientUserAdditionalData
        fields = ['shareMedicalRecord']

class ProfileDetailForTopRatedCoachesSerializer(ModelSerializer):
    otherParameters=SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'firstName', 'lastName','fullName', 'email',
                  'mobileNo', 'profileImage', 'userType', 'genderType', 'zipCode', 'dateOfBirth','state','otherParameters']

    def get_otherParameters(self,obj):
        add = RatingAndReview.objects.filter(providerId=obj.id).aggregate(Avg('providerRating'))
        params = {
            "averageRating":add["providerRating__avg"]
        }
        return params