from django.urls import path
from .views import SearchProviderSendRequest,ProviderRequestFetch,RequestStatusChange,GetProviderAfterAcceptRequest,RejectAfterTimeout,TwilioAccessTokenView,ConsultationSessionsHistory,ConsultationSessionsHistoryDetail,ConsultationSessionsHistoryProvider,ConsultationSessionsHistoryProviderDetail,ProviderRequestFetchDetail
from notification.views import NotificationListView
from searchAPIs import views
urlpatterns = [
    path('search/provider', SearchProviderSendRequest.as_view()),
    path('provider/request/fetch', ProviderRequestFetch.as_view()),
    path('provider/request/fetch/detail', ProviderRequestFetchDetail.as_view()),
    path('accept/reject/request',RequestStatusChange.as_view()),
    path('get/provider/after/accept', GetProviderAfterAcceptRequest.as_view()),
    path('reject/request/after/timeout', RejectAfterTimeout.as_view()),
    path('twilio/accessToken/generate', TwilioAccessTokenView.as_view()),
    path('notification/list', NotificationListView.as_view()),
    path('consultation/sessions/history', ConsultationSessionsHistory.as_view()),
    path('consultation/history/detail', ConsultationSessionsHistoryDetail.as_view()),
    path('consultation/history/provider',ConsultationSessionsHistoryProvider.as_view()),
    path('consultation/provider/detail',ConsultationSessionsHistoryProviderDetail.as_view()),
    path('add/call/duration', views.AddCallDuration.as_view())
]
