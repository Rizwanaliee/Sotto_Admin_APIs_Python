import django
from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from .views import (UserRegistrationView, GetAllLicenseType, UserLoginView,
                    ForgetPasswordUpdate,
                    ProfileDetail,
                    PasswordVerification,
                    UpdateMobileNo,
                    UpdateUserProfile,
                    DeleteDoc,
                    EmailOrMobileNoVerification,
                    VisibilityOnOff,
                    UserLogout,
                    ChangePasswordView,
                    CreateProviderStripeAccount,
                    LinkProviderStripeAccount,
                    ProviderStripeAccountStatusChange,
                    ProviderStripeAccountCheck,
                    )
urlpatterns = [
    path('user/registration', UserRegistrationView.as_view()),
    path('license/type/list', GetAllLicenseType.as_view()),
    path('user/login', UserLoginView.as_view()),
    path('forget/password/update', ForgetPasswordUpdate.as_view()),
    path('profile/detail', ProfileDetail.as_view()),
    path('password/verification', PasswordVerification.as_view()),
    path('update/mobileNo', UpdateMobileNo.as_view()),
    path('update/user/profile', UpdateUserProfile.as_view()),
    path('delete/doc', DeleteDoc.as_view()),
    path('email/mobileNo/verification', EmailOrMobileNoVerification.as_view()),
    path('visibility/on/off', VisibilityOnOff.as_view()),
    path('user/logout', UserLogout.as_view()),
    path('change/password', ChangePasswordView.as_view()),
    path('create/provider/stripe/account', CreateProviderStripeAccount.as_view()),
    path('generate/account/link/onboarding', LinkProviderStripeAccount.as_view()),
    path('stripe/account/change/status', ProviderStripeAccountStatusChange.as_view()),
    path('stripe/account/check',ProviderStripeAccountCheck.as_view()),
    # path('thanks/to/all/API', ThanksAll.as_view())
]