from django.shortcuts import render
from requests import delete
from rest_framework.generics import CreateAPIView, DestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import JSONParser
import jwt
from sotto_admin_apis.settings import SECRET_KEY, STRIPE_API_KEY
import stripe
from auth_APIs.models import ProviderUserAdditionalData, User
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Q
from paymentAPIs.models import SavedCardDetail, Transaction
import io
from searchAPIs.models import Consultantion, RequestAssign
from auth_APIs.models import ProviderStripeAccount
from .serializers import ProviderPrgressNoteSerailizer, TransactionCreateSerializer
from Helpers.helper import send_email
# Create your views here.


class AddCardView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=user['user_id']) & Q(userType=1)).first()

            cardNumber = pythonData.get('cardNumber', False)
            expMonth = pythonData.get('exp_month', False)
            expYear = pythonData.get('exp_year', False)
            cvv = pythonData.get('cvc', False)
            cardHolderName = pythonData.get('name', False)
            if user is None:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "User not found!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if not cardNumber:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Card number required"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if not expMonth:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Expiry month field required"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if not expYear:
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Expiry year field required"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if not cvv:
                response = {
                    "error": {
                        "errorCode": 505,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Cvv field required"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if not cardHolderName:
                response = {
                    "error": {
                        "errorCode": 508,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "cardHolderName required"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            if not user.stripeCustomerId:
                response = {
                    "error": {
                        "errorCode": 506,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Stripe CustomerId is missing!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            paymntMethodRespon = stripe.PaymentMethod.create(
                type="card",
                card={
                    "number": cardNumber,
                    "exp_month": expMonth,
                    "exp_year": expYear,
                    "cvc": cvv,
                },
                billing_details={
                    "name": cardHolderName
                }
            )
            fingerprintCheck = paymntMethodRespon["card"]["fingerprint"]
            if SavedCardDetail.objects.filter(Q(userId=user) & Q(fingerprint=fingerprintCheck)):
                response = {
                    "error": {
                        "errorCode": 507,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Card already exist!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            attactRes = stripe.PaymentMethod.attach(
                paymntMethodRespon["id"],
                customer=user.stripeCustomerId,
            )
            paymentMethodId = attactRes["id"]
            fingerPrint = attactRes["card"]["fingerprint"]
            if SavedCardDetail.objects.filter(Q(userId=user)).count() < 1:
                card = SavedCardDetail.objects.create(
                    userId=user, paymentMethodId=paymentMethodId, fingerprint=fingerPrint, cardStatus=2)
                stripe.Customer.modify(
                    user.stripeCustomerId,
                    invoice_settings={
                        "default_payment_method": paymentMethodId
                    }
                )
            else:
                card = SavedCardDetail.objects.create(
                    userId=user, paymentMethodId=paymentMethodId, fingerprint=fingerPrint)
            data = {
                "paymentMethodId": card.paymentMethodId,
                "PatientName": user.fullName
            }

            response = {
                "error": None,
                "response": {
                    "paymentMethodDetails": data,
                    "message": {
                        'success': True,
                        "successCode": 102,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Card Saved Successfully."
                    }
                }
            }
            return Response(response, status=status.HTTP_200_OK)

        except Exception as exception:
            response = {
                "error": {
                    "errorCode": 511,
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "errorMessage": str(exception)
                },
                "response": None
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        try:
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=user['user_id']) & Q(userType=1)).first()
            if user is None:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "User not found!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if not user.stripeCustomerId:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Stripe CustomerId is missing!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            res = stripe.Customer.list_payment_methods(
                user.stripeCustomerId,
                type="card",
            )
            customerDefaultCard = stripe.Customer.retrieve(
                user.stripeCustomerId)
            response = {
                "error": None,
                "response": {
                    "defaultCardId": customerDefaultCard["invoice_settings"]["default_payment_method"],
                    "paymentMethodsList": res,
                    "message": {
                        'success': True,
                        "successCode": 102,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Fetched paymentmethods details successfully."
                    }
                }
            }
            return Response(response, status=status.HTTP_200_OK)

        except Exception as exception:
            response = {
                "error": {
                    "errorCode": 511,
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "errorMessage": str(exception)
                },
                "response": None
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class CardDetachView(DestroyAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=user['user_id']) & Q(userType=1)).first()
            paymentMethodId = pythonData.get('paymentMethodId', False)
            if user is None:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "User not found!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if not user.stripeCustomerId:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Stripe CustomerId is missing!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if not paymentMethodId:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "paymentMethodId field required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            check = SavedCardDetail.objects.filter(
                Q(userId=user) & Q(paymentMethodId=paymentMethodId)).first()
            
            if not check:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "paymentMethodId invalid!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if check.cardStatus == 2:
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_400_BAD_REQUEST,
                        "errorMessage": "You can not delete default card!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            checkRes = stripe.Customer.retrieve(user.stripeCustomerId)
            if checkRes["invoice_settings"]["default_payment_method"] == paymentMethodId:

                res = stripe.PaymentMethod.detach(
                    paymentMethodId,
                )
                SavedCardDetail.objects.filter(Q(userId=user) & Q(
                    paymentMethodId=paymentMethodId)).delete()
                makDefaultMethod = SavedCardDetail.objects.filter(
                    Q(userId=user)).first()
                if SavedCardDetail.objects.filter(Q(userId=user)).count() > 0:
                    stripe.Customer.modify(
                        user.stripeCustomerId,
                        invoice_settings={
                            "default_payment_method": makDefaultMethod.paymentMethodId}
                    )
                    SavedCardDetail.objects.filter(Q(userId=user) & Q(
                        paymentMethodId=makDefaultMethod.paymentMethodId)).update(cardStatus=2)
            else:
                res = stripe.PaymentMethod.detach(
                    paymentMethodId,
                )
                SavedCardDetail.objects.filter(Q(userId=user) & Q(
                    paymentMethodId=paymentMethodId)).delete()

            response = {
                "error": None,
                "response": {
                    "message": {
                        'success': True,
                        "successCode": 102,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Card Deleted Successfully."
                    }
                }
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as exception:
            response = {
                "error": {
                    "errorCode": 511,
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "errorMessage": str(exception)
                },
                "response": None
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class MakeDefaultCardView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=user['user_id']) & Q(userType=1)).first()
            paymentMethodId = pythonData.get('paymentMethodId', False)
            if user is None:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "User not found!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if not paymentMethodId:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "paymentmethodId field is required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            if not SavedCardDetail.objects.filter(Q(userId=user) & Q(paymentMethodId=paymentMethodId)).first():
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Invalid payment method id!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if not user.stripeCustomerId:
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Stripe CustomerId is missing for this user!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            allcard = SavedCardDetail.objects.filter(userId=user).all()
            for card in allcard:
                if card.paymentMethodId == paymentMethodId:
                    stripe.Customer.modify(
                        user.stripeCustomerId,
                        invoice_settings={
                            "default_payment_method": paymentMethodId
                        }
                    )
                    card.cardStatus = 2
                    card.save()
                else:
                    card.cardStatus = 1
                    card.save()

            response = {
                "error": None,
                "response": {
                    "defaultPaymetmethodId": paymentMethodId,
                    "message": {
                        'success': True,
                        "successCode": 102,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Default Card Set Successfully."
                    }
                }
            }
            return Response(response, status=status.HTTP_200_OK)

        except Exception as exception:
            response = {
                "error": {
                    "errorCode": 511,
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "errorMessage": str(exception)
                },
                "response": None
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class CreatePaymentIntentWithNoteView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=user['user_id']) & Q(userType=2)).first()
            consultantiontId = pythonData.get('consultantiontId', False)
            callDuration = int(pythonData.get('callDuration', False))
            if user is None:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "User not found!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if not consultantiontId:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "ConsultationId required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            if not callDuration:
                response = {
                    "error": {
                        "errorCode": 505,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "callDuration required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            consult = Consultantion.objects.filter(
                Q(id=consultantiontId) & Q(consultantionStatus=2) & Q(providerId=user)).first()
            patientUser = User.objects.filter(id=consult.userId.id).first()
            if not consult:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Invalid ConsultationId!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            defalutPayementMethod = SavedCardDetail.objects.filter(
                Q(userId=patientUser) & Q(cardStatus=2)).first()
            if not defalutPayementMethod:
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Default card is missing!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            provider = ProviderUserAdditionalData.objects.filter(
                userId=user).first()
            transCheck = Transaction.objects.filter(
                Q(consultantiontId=consult) & Q(userId=patientUser) & Q(paymentStatus=1))
            if transCheck:
                response = {
                    "error": {
                        "errorCode": 507,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Payment already initiated!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            perMinutePrice = (provider.fee / 60)
            if callDuration <= 40:
                transAmmount = callDuration * perMinutePrice
            elif callDuration > 40 and callDuration <= 60:
                transAmmount = provider.fee
            else:
                transAmmount = callDuration * perMinutePrice

            res = stripe.PaymentIntent.create(
                payment_method_types=['card'],
                amount=round(transAmmount*100),
                currency='usd',
                customer=patientUser.stripeCustomerId,
                payment_method=defalutPayementMethod.paymentMethodId,
                transfer_group=f"order{consult.id}",
                metadata={
                    "consultationId": consult.id
                }
            )
            pythonData["paymentId"] = res["id"]
            pythonData["amount"] = res["amount"]/100
            pythonData["userId"] = patientUser.id
            pythonData["paymentMethodId"] = defalutPayementMethod.id
            pythonData["callDuration"] = callDuration
            pythonData["paymentStatus"] = 1
            stripeFee = ((res["amount"]/100) * 2.9 / 100) + 0.30
            netAmount = (res["amount"]/100) - (((res["amount"]/100) * 2.9 / 100) + 0.30)
            pythonData["stripeFee"] = round(stripeFee,2)
            pythonData["netAmmount"] = round(netAmount,2)
            serializer1 = TransactionCreateSerializer(data=pythonData)
            serializer2 = ProviderPrgressNoteSerailizer(data=pythonData)
            if serializer1.is_valid(raise_exception=True) and serializer2.is_valid(raise_exception=True):
                transaction = serializer1.save()
                progress = serializer2.save()
                consult.callDuration = callDuration
                consult.save()
                data = {
                    "noteDetails": {
                        "noteId": progress.id,
                        "consultantiontId": progress.consultantiontId.id,
                    },
                    "transactionDetails": {
                        "transactionId": transaction.id
                    }

                }
                User.objects.filter(id=consult.providerId.id).update(isAvailable=True)
                response = {
                    "error": None,
                    "response": {
                        "data": data,
                        "message": {
                            'success': True,
                            "successCode": 101,
                            "statusCode": status.HTTP_200_OK,
                            "successMessage": "Note submitted and transaction initiated successfully."
                        }
                    }
                }
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = {
                    "error": {
                        "errorCode": 506,
                        "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                        "errorMessage": "Error while submitting. Please try again later."
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as exception:
            response = {
                "error": {
                    "errorCode": 511,
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "errorMessage": str(exception)
                },
                "response": None
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class ConfirmPaymentWithCompletionView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=user['user_id']) & Q(userType=2)).first()
            consultantiontId = pythonData.get('consultantiontId', False)
            transactionId = pythonData.get('transactionId', False)
            if user is None:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "User not found!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if not consultantiontId:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "ConsultationId required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if not transactionId:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "transactionId required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if not Transaction.objects.filter(id=transactionId).first():
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "transaction not initiated!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            consult = Consultantion.objects.filter(
                Q(id=consultantiontId) & Q(consultantionStatus=2) & Q(providerId=user)).first()
            if not consult:
                response = {
                    "error": {
                        "errorCode": 505,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Invalid ConsultationId!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            stripeCheck = ProviderStripeAccount.objects.filter(
                Q(userId=user) & Q(isCompleted=True)).first()
            if not stripeCheck:
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Please complete payout onboarding for payment"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            trans = Transaction.objects.filter(id=transactionId).first()
            paymentMethod = SavedCardDetail.objects.filter(
                id=trans.paymentMethodId.id).first()
            res = stripe.PaymentIntent.confirm(
                trans.paymentId,
                payment_method=paymentMethod.paymentMethodId,
            )

            chargeId = res["charges"]["data"][0]["id"]
            reciptUrl = res["charges"]["data"][0]["receipt_url"]
            Transaction.objects.filter(id=transactionId).update(
                paymentStatus=2, reciept=reciptUrl)
            consult.paymentStatus = 2
            consult.consultantionStatus = 4
            consult.consultantiontFee = trans.amount
            consult.save()
            RequestAssign.objects.filter(Q(consultantiontId=consult) & Q(
                assignStatus=2)).update(assignStatus=4)
            adminCharge = trans.netAmmount * 10 / 100
            netAmmount = trans.netAmmount - adminCharge
            trans.adminCharge = round(adminCharge,2)
            trans.netAmmount = round(netAmmount,2)
            trans.paymentStatus = 2
            trans.save()
            stripe.Transfer.create(
                amount=round(netAmmount * 100),
                currency="usd",
                destination=stripeCheck.stipeAccountId,
                transfer_group=f"order{consult.id}",
                source_transaction=chargeId
            )
            response = {
                "error": None,
                "response": {
                    "message": {
                        'success': True,
                        "successCode": 102,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Payment done successfully."
                    }
                }
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as exception:
            response = {
                "error": {
                    "errorCode": 511,
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "errorMessage": str(exception)
                },
                "response": None
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
