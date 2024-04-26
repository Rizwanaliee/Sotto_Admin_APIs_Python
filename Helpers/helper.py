from sotto_admin_apis.settings import NOTIFICATION_SERVER_KEY
import requests
import json
import boto3
import os
from sotto_admin_apis import settings
import uuid
from django.core.mail import send_mail
from userManagement.models import DefaultPriceAndFeeSetting

def feeAndPriceSetting():
    setting = DefaultPriceAndFeeSetting.objects.all().first()
    return setting



def send_notification(title, message, deviceTokens, data):
    serverToken = NOTIFICATION_SERVER_KEY
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'key=' + serverToken,
    }


    body = {
        "registration_ids": deviceTokens,
        "notification": {
            "body": message,
            "title": title,
            "vibrate": 1,
            "sound": 1
        },
        "data": data
    }
    response = requests.post(
        "https://fcm.googleapis.com/fcm/send", headers=headers, data=json.dumps(body))
    data = response.json()
    if data['failure'] == 0:
        return True
    else:
        return False

def send_notification1(deviceTokens, data):
    serverToken = NOTIFICATION_SERVER_KEY
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'key=' + serverToken,
    }

    body = {
        "registration_ids": deviceTokens,
        "data": data
    }
    response = requests.post(
        "https://fcm.googleapis.com/fcm/send", headers=headers, data=json.dumps(body))
    data = response.json()
    if data['failure'] == 0:
        return True
    else:
        return False

def s3_helper(file):
    s3 = boto3.resource('s3', aws_access_key_id=settings.AWS_ACCESS_KEY, 
                              aws_secret_access_key=settings.AWS_SECRET_KEY,
                              region_name=settings.REGION_NAME
                              )

    bucket = s3.Bucket(settings.S3_BUCKET)
    split_tup = os.path.splitext(file.name)
    file_extension = split_tup[1]
    new_file_name = "image"+str(uuid.uuid4())[:8]+file_extension
    bucket.put_object(Key=new_file_name, Body=file)
    file_url = 'https://sotto-dev.s3.us-west-1.amazonaws.com/'+new_file_name
    return file_url


def send_email(email, subject, message):
    subject = subject
    message = message
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
    return True