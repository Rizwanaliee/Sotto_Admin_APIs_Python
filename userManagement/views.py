from urllib import request
from wsgiref.simple_server import demo_app
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from auth_APIs.models import User
from django.db.models import Q
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth.hashers import make_password
from searchAPIs.models import Consultantion, RequestAssign
from sotto_admin_apis import settings
from django.core.mail import send_mail
import uuid
from auth_APIs.models import ProviderUserLicenseDocs, ProviderUserAdditionalData, PatientUserAdditionalData
from django.urls import reverse
from paymentAPIs.models import Transaction
from django.db.models import Sum
from userManagement.models import DefaultPriceAndFeeSetting
# Create your views here.


def adminLogin(request):
    if request.method == "GET":
        return render(request, 'userManagement/adminLogin.html')
    else:
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(email=email, password=password)
        if user is None:
            messages.warning(request, 'Incorrect username/password')
            return redirect('admin-login')
        else:
            if user.is_superuser == 1:
                login(request, user)
                return redirect('admin-dashboard')
            else:
                messages.warning(request, 'Not authenticate user')
            return redirect('admin-login')


@login_required(login_url='admin-login')
def adminDashboard(request):
    paitentUsers = User.objects.filter(
        Q(isApproved=1) & Q(userType=1) & Q(isDeleted=False)).order_by("-id")[:2]
    patientCount = User.objects.filter(
        Q(isApproved=1) & Q(userType=1) & Q(isDeleted=False)).all().count()
    providersUsers = User.objects.filter(
        Q(isApproved=1) & Q(userType=2) & Q(isDeleted=False)).order_by("-id")[:2]

    providerCount = User.objects.filter(
        Q(isApproved=1) & Q(userType=2) & Q(isDeleted=False)).all().count()
    total_revenue_ammount = Transaction.objects.filter(
        Q(paymentStatus=2)).aggregate(Sum('amount'))['amount__sum']
    totalConsultation = Consultantion.objects.filter(
        consultantionStatus=4).all().count()
    context = {
        "patientUsers": paitentUsers,
        "providersUsers": providersUsers,
        "total_patient": patientCount,
        "total_provider": providerCount,
        "total_revenue": total_revenue_ammount,
        "total_consulltation": totalConsultation
    }
    return render(request, 'userManagement/adminDashboard.html', context)


def logoutAdmin(request):
    logout(request)
    return redirect('admin-login')

#############provider#################


class ProviderUserRequest(ListView, LoginRequiredMixin):
    model = User
    paginate_by = 20
    template_name = 'userManagement/providerUserRequests.html'
    queryset = User.objects.filter(Q(userType=2) & Q(
        isDeleted=False) & Q(isApproved__in=[1, 3])).order_by('-id')
    context_object_name = 'providerUsers'
    login_url = 'admin-login'


@login_required(login_url='admin-login')
def changeRequestStatus(request, status, userId):
    user = User.objects.filter(id=userId).first()
    if not user:
        messages.warning(request, 'Incorrect userId')
        return redirect('provider-usr-requests')
    if status == 2:
        user.isApproved = status
        user.isVerified = True
        user.save()
    if status == 3:
        user.isApproved = status
        user.isVerified = False
        user.save()
    return redirect('provider-usr-requests')


@login_required(login_url='admin-login')
def searchUserRequest(request):
    try:
        search_key = request.POST.get('q')
        query1 = Q(fullName__icontains=search_key) | Q(
            email__icontains=search_key) | Q(
            mobileNo__icontains=search_key)
        users = User.objects.filter((Q(query1) & Q(userType=2) & Q(
            isDeleted=False) & Q(isApproved__in=[1, 3]))).all().order_by('-id')
        paginator = Paginator(users, 20)
        page = request.GET.get('page')
        page_obj = paginator.get_page(page)
        context = {
            'providerUsers': users,
            'page_obj': page_obj,
            'InputText': search_key
        }
        return render(request, 'userManagement/providerUserRequests.html', context)
    except Exception as e:
        return redirect('provider-usr-requests')


@login_required(login_url='admin-login')
def filterByStatus(request):
    status = request.POST.get('filter_status_id')
    users = User.objects.filter(Q(userType=2) & Q(
        isDeleted=False) & Q(isApproved=status)).all().order_by('-id')
    paginator = Paginator(users, 20)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    context = {
        'providerUsers': users,
        'page_obj': page_obj,
        'SelectedType': status
    }
    return render(request, 'userManagement/providerUserRequests.html', context)


class ProviderApprovedUsers(ListView, LoginRequiredMixin):
    model = User
    paginate_by = 20
    template_name = 'userManagement/providerApprovedUsers.html'
    queryset = User.objects.filter(Q(userType=2) & Q(
        isDeleted=False) & Q(isApproved=2)).order_by('-id')
    context_object_name = 'approvedUsers'
    login_url = 'admin-login'


@login_required(login_url='admin-login')
def blockUnblock(request, userId):
    user = User.objects.get(id=userId)
    if(user.isActive == True):
        user.isActive = False
        user.save()
        if user.userType == 1:
            res = reverse('patient-users')
        else:
            res = reverse('approved-users-provider')
        if 'page' in request.GET:
            res += f"?page={request.GET['page']}"
        return redirect(res)
    else:
        user.isActive = True
        user.save()
        if user.userType == 1:
            res = reverse('patient-users')
        else:
            res = reverse('approved-users-provider')
        if 'page' in request.GET:
            res += f"?page={request.GET['page']}"
        return redirect(res)


@login_required(login_url='admin-login')
def deleteUser(request):
    userId = request.POST.get('user_id')
    user = User.objects.filter(id=userId).first()
    if user.userType == 1:
        user.isDeleted = True
        user.save()
        return redirect('patient-users')
    else:
        user.isDeleted = True
        user.save()
        if user.isApproved == 1:
            return redirect('provider-usr-requests')
        else:
            return redirect('approved-users-provider')


@login_required(login_url='admin-login')
def searchUserApproved(request):
    try:
        search_key = request.POST.get('q')
        query1 = Q(fullName__icontains=search_key) | Q(
            email__icontains=search_key) | Q(
            mobileNo__icontains=search_key)
        users = User.objects.filter((Q(query1) & Q(userType=2) & Q(
            isDeleted=False) & Q(isApproved=2))).all().order_by('-id')
        paginator = Paginator(users, 20)
        page = request.GET.get('page')
        page_obj = paginator.get_page(page)
        context = {
            'approvedUsers': users,
            'page_obj': page_obj,
            'InputText': search_key
        }
        return render(request, 'userManagement/providerApprovedUsers.html', context)
    except Exception as e:
        return redirect('approved-users-provider')


def filterByStatusApproved(request):
    status = request.POST.get('filter_status_id')
    users = User.objects.filter(Q(userType=2) & Q(
        isDeleted=False) & Q(isApproved=2) & Q(isActive=status)).all().order_by('-id')
    paginator = Paginator(users, 20)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    context = {
        'approvedUsers': users,
        'page_obj': page_obj,
        'SelectedType': status
    }
    return render(request, 'userManagement/providerApprovedUsers.html', context)

#### patient user ################################


class PatientUsers(ListView, LoginRequiredMixin):
    model = User
    paginate_by = 20
    template_name = 'userManagement/patientUsers.html'
    queryset = User.objects.filter(Q(userType=1) & Q(
        isDeleted=False)).all().order_by('-id')
    context_object_name = 'patientUsers'
    login_url = 'admin-login'


@login_required(login_url='admin-login')
def searchUserPetient(request):
    try:
        search_key = request.POST.get('q')
        query1 = Q(fullName__icontains=search_key) | Q(
            email__icontains=search_key) | Q(
            mobileNo__icontains=search_key)
        users = User.objects.filter((Q(query1) & Q(userType=1) & Q(
            isDeleted=False))).all().order_by('-id')
        paginator = Paginator(users, 20)
        page = request.GET.get('page')
        page_obj = paginator.get_page(page)
        context = {
            'patientUsers': users,
            'page_obj': page_obj,
            'InputText': search_key
        }
        return render(request, 'userManagement/patientUsers.html', context)
    except Exception as e:
        return redirect('approved-users-provider')


def filterByStatusActiveBlock(request):
    status = request.POST.get('filter_status_id')
    users = User.objects.filter(Q(userType=1) & Q(
        isDeleted=False) & Q(isActive=status)).all().order_by('-id')
    paginator = Paginator(users, 20)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    context = {
        'patientUsers': users,
        'page_obj': page_obj,
        'SelectedType': status
    }
    return render(request, 'userManagement/patientUsers.html', context)


def send_email_forget_pass(email, token):
    subject = 'Your forget password link'
    message = f'Hi, click on the link and reset the password {settings.BASE_URL}/admin-change-password/{token}/'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
    return True

@login_required(login_url='admin-login')
def admin_forget_password(request):
    if(request.method == 'GET'):
        return render(request, 'userManagement/admin_forget_pass.html')
    else:
        email = request.POST.get('email')
        if not User.objects.filter(Q(email=email) & Q(is_superuser=True)).first():
            messages.warning(request, 'User Not Found')
            return redirect('admin-forget-password')
        user_obj = User.objects.get(email=email)
        token = str(uuid.uuid4())
        user_obj.admin_forget_password_token = token
        user_obj.save()
        send_email_forget_pass(user_obj.email, token)
        messages.success(
            request, 'An email has been sent please check your email account')
        return redirect('admin-login')

@login_required(login_url='admin-login')
def admin_change_password(request, token):
    if(request.method == 'GET'):
        obj = User.objects.get(admin_forget_password_token=token)
        Context = {"user_id": obj.id}
        return render(request, 'userManagement/admin-change-password.html', Context)
    else:
        new_password = request.POST.get('new_pass')
        confirm_new_pass = request.POST.get('confirm_new_pass')
        user_id = User.objects.get(admin_forget_password_token=token)
        if not user_id:
            messages.warning(request, 'User not found')
            return redirect('set-new-admin-password', user_id.admin_forget_password_token)
        if new_password != confirm_new_pass:
            messages.warning(
                request, 'Password & confirm password does not match')
            return redirect('set-new-admin-password', user_id.admin_forget_password_token)
        user_obj = User.objects.get(id=user_id.id)
        user_obj.set_password(new_password)
        user_obj.save()
        messages.success(request, 'Your password successfully updated')
        return redirect('admin-login')


@login_required(login_url='admin-login')
def patientDetailPage(request, patientId):
    patient = User.objects.filter(id=patientId).first()
    if not patient:
        return redirect('patient-users')
    return render(request, 'userManagement/patientUserDetail.html', {"User": patient})


@login_required(login_url='admin-login')
def providerDetailPage(request, providerId):
    provider = User.objects.filter(id=providerId).first()
    licenseDocs = ProviderUserLicenseDocs.objects.filter(userId=provider).all()
    if not provider:
        return redirect('provider-usr-requests')
    context = {
        "User": provider,
        "Docs": licenseDocs
    }
    return render(request, 'userManagement/providerUserDetail.html', context)


class ConsultaionView(ListView, LoginRequiredMixin):
    model = User
    paginate_by = 20
    template_name = 'userManagement/consultationView.html'

    def get_queryset(self):
        providerIds = RequestAssign.objects.filter(
            assignStatus__in=[2, 3, 4, 5, 6, 7]).values_list('providerId', flat=True)
        queryset = User.objects.filter(id__in=providerIds).order_by('-id')
        return queryset
    login_url = 'admin-login'
    context_object_name = 'providers'


@login_required(login_url='admin-login')
def priceAndFeeSetting(request):
    if request.method == "GET":
        settingVal = DefaultPriceAndFeeSetting.objects.all().first()
        return render(request, 'userManagement/priceAndFeeSetting.html', {"settingValues":settingVal})
    else:
        providerFee = request.POST.get("providerFee")
        minPrice = request.POST.get("patinetMinPrice")
        maxPrice = request.POST.get("patientMaxPrice")
        settingVal = DefaultPriceAndFeeSetting.objects.all().first()
        providerIds = ProviderUserAdditionalData.objects.filter(userId__isDeleted = False).all()
        patientIds = PatientUserAdditionalData.objects.filter(userId__isDeleted = False).all()
        if providerIds:
            if int(settingVal.fee) != int(providerFee):
                for providerData in providerIds:
                    providerData.fee = providerFee
                    providerData.save()
        if patientIds:
            if int(settingVal.minPrice) != int(minPrice) or int(settingVal.maxPrice) != int(maxPrice):
                for patinetData in patientIds:
                    patinetData.minPrice = minPrice
                    patinetData.maxPrice = maxPrice
                    patinetData.save()
        
        settingVal.fee = providerFee
        settingVal.minPrice = minPrice
        settingVal.maxPrice = maxPrice
        settingVal.save()
        
        messages.success(request, "All users price and fee successfully updated!!")
        return redirect('price-fee-setting')

def refreshUrlView(request):
    return render(request, 'userManagement/refreshUrl.html')

def returnUrlView(request):
    return render(request, 'userManagement/returnUrl.html')


