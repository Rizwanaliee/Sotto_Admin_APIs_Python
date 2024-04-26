from django.urls import path
from revenueManagement import views
urlpatterns = [
    path('providers/', views.providersForRevenueList, name='providers-list-for-revenue'),
    path('revenue-view-detail/<int:providerId>/', views.revenueViewDetail, name='revenue-view-detail'),
    path('provider-search/',views.providerSearchInList, name='provider-serch-revenue'),
    path('transaction-search-patient/<int:providerId>/',views.transactionSearch, name='transaction-search-patient'),
]
