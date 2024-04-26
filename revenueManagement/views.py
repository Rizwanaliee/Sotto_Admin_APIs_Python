from django.shortcuts import render
from django.core.paginator import Paginator
from auth_APIs.models import User
from django.db.models import Q
from django.db.models import Sum
from paymentAPIs.models import Transaction

# Create your views here.
def providersForRevenueList(request):
    users =  User.objects.filter(Q(userType=2) & Q(isDeleted=False)).all().order_by("-id")
    total_revenue_ammount = Transaction.objects.filter(Q(paymentStatus=2)).aggregate(Sum('amount'))['amount__sum']
    paginator = Paginator(users,20)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    context = {
        'providers_users': users,
        'page_obj': page_obj,
        'total_ammount':total_revenue_ammount
    }
    return render(request,'revenueManagement/revenueProvidersList.html', context)


def revenueViewDetail(request, providerId):
    provider = User.objects.get(id=providerId)
    trans = Transaction.objects.filter(Q(paymentStatus=2) & Q(consultantiontId__providerId=provider)).all().order_by("-id")
    total_revenue_ammount = Transaction.objects.filter(Q(paymentStatus=2) & Q(consultantiontId__providerId=provider)).aggregate(Sum('amount'))['amount__sum']
    paginator = Paginator(trans,20)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    context = {
        'provider':provider,
        'providers_trans': trans,
        'page_obj': page_obj,
        'total_ammount':total_revenue_ammount
    }
    return render(request,'revenueManagement/revenueViewDetail.html', context)

def providerSearchInList(request):
    search_key = request.POST.get('q')
    total_revenue_ammount = Transaction.objects.filter(Q(paymentStatus=2)).aggregate(Sum('amount'))['amount__sum']
    provider = User.objects.filter(Q(userType=2) & Q(isDeleted=False) & Q(Q(fullName__icontains = search_key)) | Q(mobileNo__icontains = search_key)).all().order_by("-id")
    paginator = Paginator(provider, 20)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    context = {
        'providers_users': provider,
        'page_obj': page_obj,
        'total_ammount':total_revenue_ammount,
        'InputText':search_key
    }
    return render(request,'revenueManagement/revenueProvidersList.html', context)

def transactionSearch(request,providerId):
    search_key = request.POST.get('q')
    provider = User.objects.get(id=providerId)
    total_revenue_ammount = Transaction.objects.filter(Q(paymentStatus=2)).aggregate(Sum('amount'))['amount__sum']
    trans = Transaction.objects.filter(Q(paymentStatus=2) & Q(consultantiontId__providerId=provider) & Q(Q(consultantiontId__userId__fullName__icontains = search_key)) | Q(consultantiontId__userId__mobileNo__icontains = search_key)).all().order_by("-id")
    paginator = Paginator(trans, 20)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    context = {
        'provider':provider,
        'providers_trans': trans,
        'page_obj': page_obj,
        'InputText':search_key,
        'total_ammount':total_revenue_ammount
    }
    return render(request,'revenueManagement/revenueViewDetail.html', context)