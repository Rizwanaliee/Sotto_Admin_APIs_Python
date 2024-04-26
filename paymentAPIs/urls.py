from django.urls import path
from paymentAPIs import views

urlpatterns = [
    path('add/card/get/list', views.AddCardView.as_view()),
    path('detach/paymentmethod', views.CardDetachView.as_view()),
    path('set/default/card', views.MakeDefaultCardView.as_view()),
    path('create/note/with/payment/', views.CreatePaymentIntentWithNoteView.as_view()),
    path('confirm/payment/complete/consultation', views.ConfirmPaymentWithCompletionView.as_view())
]
