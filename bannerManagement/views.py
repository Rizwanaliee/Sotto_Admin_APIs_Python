from django.shortcuts import render, redirect
from django.views.generic import ListView
# from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Banner
from Helpers.helper import s3_helper
from django.contrib import messages
from auth_APIs.models import User
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.response import Response
from notification.models import Notifications
from sotto_admin_apis.settings import SECRET_KEY, NOTIFICATION_SERVER_KEY
import jwt
from auth_APIs.models import User
from django.db.models import Q
from .serializers import BannerListSerializer
import os

# Create your views here.


class BannerListView(ListView, LoginRequiredMixin):
    model = Banner
    paginate_by = 20
    template_name = 'bannerManagement/bannerList.html'
    queryset = Banner.objects.all().order_by('-id')
    context_object_name = 'bannerObjects'
    login_url = 'admin-login'


def addBanner(request):
    if request.method == "GET":
        return render(request, 'bannerManagement/addBanner.html')
    else:
        title = request.POST.get("title")
        image = request.FILES['bannerImage']
        if image.size/1000 < 20:
            messages.warning(request, 'Image size should not less than 20 kb')
            return redirect('add-banner-view')
        Banner.objects.create(title=title, imageUrl=s3_helper(image))
        return redirect('banners-list')


def deleteBanner(request):
    bannerId = request.POST.get('banner_id')
    Banner.objects.filter(id=bannerId).delete()
    return redirect('banners-list')

# API

class BannerListAPI(ListAPIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        try:
            notifications = Banner.objects.all().order_by('-id')
            serializer = BannerListSerializer(data=notifications, many=True)
            serializer.is_valid()
            response = {
                "error": None,
                "response": {

                    "bannerData": serializer.data,

                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Banner List Fetched Successfully"
                    }
                }
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            status_code = status.HTTP_400_BAD_REQUEST
            response = {
                "error": {
                    "errorCode": 616,
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "errorMessage": str(e)
                },
                "response": None
            }
            return Response(response, status=status_code)
