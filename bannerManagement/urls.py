import imp
from django.urls import path
from bannerManagement import views
urlpatterns = [
    path('banner-list/', views.BannerListView.as_view(), name='banners-list'),
    path('add-banner/', views.addBanner, name='add-banner-view'),
    path('delete-banner/', views.deleteBanner, name='banner-delete'),
    path('banner/list', views.BannerListAPI.as_view())
]
