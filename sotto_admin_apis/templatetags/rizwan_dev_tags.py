from django import template
from auth_APIs.models import ProviderUserAdditionalData, licenseType
from datetime import datetime
from django.db.models import Q
from searchAPIs.models import Consultantion,RequestAssign
from paymentAPIs.models import Transaction
from django.db.models import Sum
register = template.Library()


@register.simple_tag
def licenseTypeDetails(userId):
    providerAdditionalData = ProviderUserAdditionalData.objects.filter(userId=userId).first()
    return providerAdditionalData

@register.simple_tag
def trimDate(date):
    date=datetime.date(date).strftime('%Y-%m-%d')
    return date

@register.simple_tag
def consultationCount(providerId,status):
    count = RequestAssign.objects.filter(Q(providerId=providerId) & Q(assignStatus=status)).all().count()
    return count

@register.simple_tag
def consultationCount2(providerId,status1, status2):
    count = RequestAssign.objects.filter(Q(providerId=providerId) & Q(assignStatus__in=[status1,status2])).all().count()
    return count
@register.simple_tag
def totalTransAmmount(providerId):
    transAmmount = Transaction.objects.filter(Q(paymentStatus=2) & Q(consultantiontId__providerId=providerId)).aggregate(Sum('amount'))['amount__sum']
    return transAmmount