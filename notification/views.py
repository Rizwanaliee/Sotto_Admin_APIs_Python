from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from auth_APIs.models import User
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.response import Response
from notification.models import Notifications
from sotto_admin_apis.settings import SECRET_KEY, NOTIFICATION_SERVER_KEY
import jwt
from auth_APIs.models import User
from django.db.models import Q
from .serializers import NotificationSerializer
from django.core.paginator import Paginator
from django.contrib import messages
from Helpers.helper import send_notification, s3_helper


# Create your views here.
class ProviderNotificationList(ListView, LoginRequiredMixin):
    model = User
    paginate_by = 20
    template_name = 'notification/providerNotificationList.html'
    queryset = Notifications.objects.filter(
        Q(notificationFor=3) & Q(notificationType=1)).all().order_by("-id")
    context_object_name = 'ProviderNotifications'
    login_url = 'admin-login'


def searchNotiProvider(request):
    search_key = request.POST.get('q')
    noti = Notifications.objects.filter(Q(notificationFor=3) & Q(notificationType=1) & Q(
        userId__fullName__icontains=search_key)).all().order_by('-id')
    paginator = Paginator(noti, 20)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    context = {
        'ProviderNotifications': noti,
        'page_obj': page_obj,
        'InputText': search_key
    }
    return render(request, 'notification/providerNotificationList.html', context)


class PatientNotificationList(ListView, LoginRequiredMixin):
    model = User
    paginate_by = 20
    template_name = 'notification/patientNotificationList.html'
    queryset = Notifications.objects.filter(
        Q(notificationFor=2) & Q(notificationType=1)).all().order_by('-id')
    context_object_name = 'PatientNotifications'
    login_url = 'admin-login'


def searchNotiPatient(request):
    search_key = request.POST.get('q')
    noti = Notifications.objects.filter(Q(notificationFor=2) & Q(notificationType=1) & Q(
        userId__fullName__icontains=search_key)).all().order_by('-id')
    paginator = Paginator(noti, 20)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    context = {
        'PatientNotifications': noti,
        'page_obj': page_obj,
        'InputText': search_key
    }
    return render(request, 'notification/patientNotificationList.html', context)


def providerPushNotification(request):
    if request.method == "GET":
        users = User.objects.filter(Q(userType=2) & Q(
            isDeleted=False)).all().order_by("-id")
        context = {
            "providers": users
        }
        return render(request, 'notification/providerPushNotification.html', context)
    else:
        if request.POST.get("rradio") == "select-provider":
            user_ids = request.POST.getlist('users_ids[]')
            if not user_ids:
                messages.warning(request, 'Please select providers!!')
                return redirect('push-notification-provider')
            title = request.POST.get('title')
            message = request.POST.get('message')
            image = request.FILES.get('notiImage')
            if image:
                imageUrl = s3_helper(image)
            else:
                imageUrl = None
            data = {
                "imageUrl": imageUrl
            }

            for user_id in user_ids:
                tokens = []
                user = User.objects.filter(id=user_id).first()
                tokens.append(user.deviceToken)
                res = send_notification(title, message, tokens, data)
                if res:
                    Notifications.objects.create(
                        title=title, message=message, imageUrl=imageUrl, userId=user, notificationFor=3, notificationType=1)
            messages.success(request, 'Notification sent successfully!!')
            return redirect('provider-noti-list')
        elif request.POST.get('rradio') == "allcustomer":
            user_ids = User.objects.filter(
                Q(userType=2) & Q(isDeleted=False)).all()
            title = request.POST.get('title')
            message = request.POST.get('message')
            image = request.FILES.get('notiImage')
            if image:
                imageUrl = s3_helper(image)
            else:
                imageUrl = None
            data = {
                "imageUrl": imageUrl
            }

            for user in user_ids:
                tokens = []
                # user = User.objects.filter(id=user_id).first()
                tokens.append(user.deviceToken)
                res = send_notification(title, message, tokens, data)
                if res:
                    Notifications.objects.create(
                        title=title, message=message, imageUrl=imageUrl, userId=user, notificationFor=3, notificationType=1)
            messages.success(request, 'Notification sent successfully!!')
            return redirect('provider-noti-list')
        elif request.POST.get('rradio') == "androidcustomer":
            user_ids = User.objects.filter(Q(userType=2) & Q(
                isDeleted=False) & Q(deviceType=1)).all()
            title = request.POST.get('title')
            message = request.POST.get('message')
            image = request.FILES.get('notiImage')
            if image:
                imageUrl = s3_helper(image)
            else:
                imageUrl = None
            data = {
                "imageUrl": imageUrl
            }

            for user in user_ids:
                tokens = []
                # user = User.objects.filter(id=user_id).first()
                tokens.append(user.deviceToken)
                res = send_notification(title, message, tokens, data)
                if res:
                    Notifications.objects.create(
                        title=title, message=message, imageUrl=imageUrl, userId=user, notificationFor=3, notificationType=1)
            messages.success(request, 'Notification sent successfully!!')
            return redirect('provider-noti-list')

        elif request.POST.get('rradio') == "ioscustomer":
            user_ids = User.objects.filter(Q(userType=2) & Q(
                isDeleted=False) & Q(deviceType=2)).all()
            title = request.POST.get('title')
            message = request.POST.get('message')
            image = request.FILES.get('notiImage')
            imageUrl = None
            if image:
                imageUrl = s3_helper(image)
            else:
                imageUrl = None
            data = {
                "imageUrl": imageUrl
            }

            for user in user_ids:
                tokens = []
                # user = User.objects.filter(id=user_id).first()
                tokens.append(user.deviceToken)
                res = send_notification(title, message, tokens, data)
                if res:
                    Notifications.objects.create(
                        title=title, message=message, imageUrl=imageUrl, userId=user, notificationFor=3, notificationType=1)
            messages.success(request, 'Notification sent successfully!!')
            return redirect('provider-noti-list')
        else:
            return redirect('push-notification-provider')


def patientPushNotification(request):
    if request.method == "GET":
        users = User.objects.filter(Q(userType=1) & Q(
            isDeleted=False)).all().order_by("-id")
        context = {
            "providers": users
        }
        return render(request, 'notification/patientPushNotification.html', context)

    else:
        if request.POST.get("rradio") == "select-provider":
            user_ids = request.POST.getlist('users_ids[]')
            if not user_ids:
                messages.warning(request, 'Please select providers!!')
                return redirect('push-notification-patient')
            title = request.POST.get('title')
            message = request.POST.get('message')
            image = request.FILES.get('notiImage')
            if image:
                imageUrl = s3_helper(image)
            else:
                imageUrl = None
            data = {
                "imageUrl": imageUrl
            }

            for user_id in user_ids:
                tokens = []
                user = User.objects.filter(id=user_id).first()
                tokens.append(user.deviceToken)
                res = send_notification(title, message, tokens, data)
                if res:
                    Notifications.objects.create(
                        title=title, message=message, imageUrl=imageUrl, userId=user, notificationFor=2, notificationType=1)
            messages.success(request, 'Notification sent successfully!!')
            return redirect('patient-noti-list')
        elif request.POST.get('rradio') == "allcustomer":
            user_ids = User.objects.filter(
                Q(userType=2) & Q(isDeleted=False)).all()
            title = request.POST.get('title')
            message = request.POST.get('message')
            image = request.FILES.get('notiImage')
            if image:
                imageUrl = s3_helper(image)
            else:
                imageUrl = None
            data = {
                "imageUrl": imageUrl
            }

            for user in user_ids:
                tokens = []
                # user = User.objects.filter(id=user_id).first()
                tokens.append(user.deviceToken)
                res = send_notification(title, message, tokens, data)
                if res:
                    Notifications.objects.create(
                        title=title, message=message, imageUrl=imageUrl, userId=user, notificationFor=2, notificationType=1)
            messages.success(request, 'Notification sent successfully!!')
            return redirect('patient-noti-list')
        elif request.POST.get('rradio') == "androidcustomer":
            user_ids = User.objects.filter(Q(userType=2) & Q(
                isDeleted=False) & Q(deviceType=1)).all()
            title = request.POST.get('title')
            message = request.POST.get('message')
            image = request.FILES.get('notiImage')
            if image:
                imageUrl = s3_helper(image)
            else:
                imageUrl = None
            data = {
                "imageUrl": imageUrl
            }

            for user in user_ids:
                tokens = []
                # user = User.objects.filter(id=user_id).first()
                tokens.append(user.deviceToken)
                res = send_notification(title, message, tokens, data)
                if res:
                    Notifications.objects.create(
                        title=title, message=message, imageUrl=imageUrl, userId=user, notificationFor=2, notificationType=1)
            messages.success(request, 'Notification sent successfully!!')
            return redirect('patient-noti-list')

        elif request.POST.get('rradio') == "ioscustomer":
            user_ids = User.objects.filter(Q(userType=2) & Q(
                isDeleted=False) & Q(deviceType=2)).all()
            title = request.POST.get('title')
            message = request.POST.get('message')
            image = request.FILES.get('notiImage')
            imageUrl = None
            if image:
                imageUrl = s3_helper(image)
            else:
                imageUrl = None
            data = {
                "imageUrl": imageUrl
            }

            for user in user_ids:
                tokens = []
                # user = User.objects.filter(id=user_id).first()
                tokens.append(user.deviceToken)
                res = send_notification(title, message, tokens, data)
                if res:
                    Notifications.objects.create(
                        title=title, message=message, imageUrl=imageUrl, userId=user, notificationFor=2, notificationType=1)
            messages.success(request, 'Notification sent successfully!!')
            return redirect('patient-noti-list')
        else:
            return redirect('push-notification-patient')


###################################### Notification APIs #######################################

class NotificationListView(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            userId = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=userId['user_id'])).first()
            if user is None:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "user not found!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            notifications = Notifications.objects.filter(Q(userId=user) & Q(notificationType=1)).all().order_by('-id')
            serializer = NotificationSerializer(data=notifications, many=True)
            serializer.is_valid()
            response = {
                "error": None,
                "response": {

                    "notifications": serializer.data,

                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Notification List Fetched Successfully"
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
