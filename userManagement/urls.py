from django.urls import path
from userManagement import views
urlpatterns = [
    ###provider
    path('',views.adminLogin, name='admin-login'),
    path('admin-forget-password/', views.admin_forget_password,name = "admin-forget-password"),
    path('admin-change-password/<token>/', views.admin_change_password, name='set-new-admin-password'),
    path('admin-dashboard/', views.adminDashboard, name="admin-dashboard"),
    path('logout',views.logoutAdmin, name="logout-admin"),
    path('provider-user-requests/', views.ProviderUserRequest.as_view(), name='provider-usr-requests'),
    path('request-status-change/<int:status>/<int:userId>/', views.changeRequestStatus, name='change-status-user'),
    path('search-provider/', views.searchUserRequest, name='provider-search'),
    path('filter-by-status/', views.filterByStatus, name='filter-by-status'),
    path('approved-providers/', views.ProviderApprovedUsers.as_view(), name='approved-users-provider'),
    path('block-unblock/<int:userId>/', views.blockUnblock, name='block-unblock'),
    path('search-approved-user/', views.searchUserApproved, name='search-approved-user'),
    path('filter-active-block/', views.filterByStatusApproved, name='active-block-filter'),
    path('provider-user-detail/<int:providerId>/', views.providerDetailPage, name='provider-detail-page'),
    ####patient user
    path('patient-users/', views.PatientUsers.as_view(), name='patient-users'),
    path('search-patient-user/', views.searchUserPetient, name='patient-user-search'),
    path('filter-active-block-patient/', views.filterByStatusActiveBlock, name='patient-act-block-filter'),
    path('patient-detail/<int:patientId>/', views.patientDetailPage, name='patient-detail-page'),
    path('delete-user/', views.deleteUser, name='delete-user'),
    ##consultatio urls
    path('consultaion-list/', views.ConsultaionView.as_view(), name="consultions-list"),
    ##setting module
    path('price-and-fee-seetings/', views.priceAndFeeSetting, name='price-fee-setting'),

    ###stripe refresh or return URLs
    path('refresh-page-view', views.refreshUrlView, name='refresh-url-view'),
    path('return-page-view', views.returnUrlView, name='return-url-view')
]
