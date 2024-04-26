
from django.contrib import admin
from django.urls import path, include # new
from django.conf.urls import url
from django.views.static import serve
from sotto_admin_apis import settings
from django.views.generic import RedirectView
from django.conf.urls.static import static

urlpatterns = [
    # url(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    # url(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
    # path('admin/', admin.site.urls),
    path('favicon.ico', RedirectView.as_view(url='/static/assets/dist/img/SOTTO.png')),
    # url(r'^favicon\.ico$',RedirectView.as_view(url='/static/assets/dist/img/SOTTO.png')),
    path('v1/api/', include('auth_APIs.urls')),
    path('',include('userManagement.urls')),
    path('v1/api/', include('searchAPIs.urls')),
    path('notification/', include('notification.urls')),
    path('revenue/', include('revenueManagement.urls')),
    path('v1/api/', include('paymentAPIs.urls')),
    path('v1/api/',include('ratingAndReview.urls')),
    path('v1/api/', include('bannerManagement.urls')),
    path('banner/', include('bannerManagement.urls'))

]
