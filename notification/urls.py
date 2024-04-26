from django.urls import path
from .views import (ProviderNotificationList, PatientNotificationList,
                    providerPushNotification,
                    patientPushNotification,
                    searchNotiProvider,
                    searchNotiPatient
                    )
urlpatterns = [
    path('provider-notification-list/',
         ProviderNotificationList.as_view(), name='provider-noti-list'),
    path('patient-notification-list/',
         PatientNotificationList.as_view(), name='patient-noti-list'),
    path('provider-push-notification/', providerPushNotification,
         name='push-notification-provider'),
    path('patient-push-notification/', patientPushNotification,
         name='push-notification-patient'),
    path('provider-notification-search/', searchNotiProvider, name="search-povider-noti"),
    path('patient-notification-search/', searchNotiPatient, name='seach-noti-patient')
]
