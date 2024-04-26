from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import JSONParser
import io
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from sotto_admin_apis.settings import SECRET_KEY
import jwt
from auth_APIs.models import PatientUserAdditionalData, User, ProviderUserAdditionalData, ProviderStripeAccount
from django.db.models import Q
from searchAPIs.models import Consultantion, RequestAssign, ProviderProgressNote
from searchAPIs.serializers import RequestAssignSerializer, ProviderAdditionalDataSerializer2, ConsultationDetailSessionHistorySerializer, ProviderAdditionalDataSerializer3, ConsultationDetailSessionHistorProviderySerializer
from sotto_admin_apis.settings import TWILIO_ACCOUNT_SID, TWILIO_API_KEY_SID, TWILIO_API_KEY_SECRET
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VideoGrant
from Helpers.helper import send_notification, send_notification1
from notification.models import Notifications
import uuid
from paymentAPIs.models import SavedCardDetail, Transaction
from auth_APIs.serializers import ProfileDetailSerializer
from paymentAPIs.serializers import ProviderPrgressNoteSerailizer
from ratingAndReview.models import FavouriteProvider, RatingAndReview
from django.db.models import Avg
from ratingAndReview.serialzers import RatingAndReviewForDetailSerializer, RatingAndReviewForDetailSerializer2, RatingAndReviewSerializer
from userManagement.models import DefaultPriceAndFeeSetting
# from twilio.rest import Client

# Create your views here.


class SearchProviderSendRequest(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            # therapyType = pythonData.get('therapyType', False)
            gender = pythonData.get('genderType', False)
            Radius = pythonData.get('radius', False)
            minFee = pythonData.get('minFee', False)
            maxFee = pythonData.get('maxFee', False)
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=user['user_id']) & Q(userType=1)).first()
            patientState = user.state
            addtionalPatient = DefaultPriceAndFeeSetting.objects.all().first()
            if gender:
                paramGender = [gender]
            else:
                paramGender = [1, 2, 3]
            if maxFee:
                minPrice = minFee
                maxPrice = maxFee
            else:
                minPrice = addtionalPatient.minPrice
                maxPrice = addtionalPatient.maxPrice

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
            # if not therapyType:
            #     response = {
            #         "error": {
            #             "errorCode": 502,
            #             "statusCode": status.HTTP_404_NOT_FOUND,
            #             "errorMessage": "TherapyType field is required"
            #         },
            #         "response": None
            #     }
            #     return Response(response, status=status.HTTP_404_NOT_FOUND)
            if not Radius:
                response = {
                    "error": {
                        "errorCode": 505,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Radius field is required"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if SavedCardDetail.objects.filter(userId=user).all().count() == 0:
                response = {
                    "error": {
                        "errorCode": 506,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Payment method not added please add credit card first!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            # licenseTypes = licenseType.objects.filter(
            #     therapyType=therapyType).values_list('id', flat=True)
            # if not licenseTypes:
            #     response = {
            #         "error": {
            #             "errorCode": 504,
            #             "statusCode": status.HTTP_404_NOT_FOUND,
            #             "errorMessage": "Wrong therapyType please check!"
            #         },
            #         "response": None
            #     }
            #     return Response(response, status=status.HTTP_404_NOT_FOUND)
            # latitude = user.lat
            # longitude = user.lng
            # limit = 5000
            # radius = Radius
            # query = """SELECT id ,( 6371 * acos( cos( radians(%2f) ) * cos( radians( lat ) ) * cos( radians( lng ) - radians(%2f) ) + sin( radians(%2f) ) * sin(radians(lat)) ) ) AS distance FROM users HAVING distance < %2f ORDER BY distance asc LIMIT 0, %d""" % (
            #     float(latitude),
            #     float(longitude),
            #     float(latitude),
            #     radius,
            #     limit
            # )
            # usersQuerySet = User.objects.raw(query)
            # user_Ids = []
            # for user_id in usersQuerySet:
            #     user_Ids.append(user_id.id)
            userCollection = User.objects.filter(Q(userType=2) & Q(isActive=True) & Q(
                isVerified=True) & Q(isAvailable=True) & Q(isApproved=2) & Q(genderType__in=paramGender) & Q(state__icontains=patientState)).values_list('id', flat=True)

            userids = ProviderUserAdditionalData.objects.filter(Q(
                userId__in=userCollection) & Q(fee__lte=maxPrice) & Q(fee__gte=minPrice)).values_list('userId', flat=True)

            if not userids:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Providers not found!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            stripeCheck = ProviderStripeAccount.objects.filter(
                Q(userId__in=userids) & Q(isCompleted=True)).all()
            if not stripeCheck:
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Providers not found due to stripe account incomplete!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            check = Consultantion.objects.filter(
                Q(userId=user) & Q(consultantionStatus=1)).first()
            if check:
                requests = RequestAssign.objects.filter(
                    Q(consultantiontId=check) & Q(assignStatus=1)).all()
                for request in requests:
                    request.assignStatus = 3
                    request.save()
                Consultantion.objects.filter(id=check.id).update(
                    consultantionStatus=3)

            consId = Consultantion.objects.create(
                consultantionStatus=1, userId=user, paymentStatus=1)
            users = User.objects.filter(id__in=userids).all()
            if not RequestAssign.objects.filter(Q(consultantiontId=consId) & Q(providerId__in=userids) & Q(assignStatus=1)):
                for usr in users:
                    title = "Consultation request!!!"
                    message = "Dear provider you have recieved consultation request!"
                    deviceToken = [usr.deviceToken]
                    data1 = {
                        "requestNotification": "requestNotification"
                    }
                    RequestAssign.objects.create(
                        consultantiontId=consId, providerId=usr)
                    res = send_notification(title, message, deviceToken, data1)
            data = {
                "consultationId": consId.id,
            }
            response = {
                "error": None,
                "response": {
                    "Data": data,
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Requests sent successfully to nearby providers!"
                    }
                }
            }
            return Response(response, status=status.HTTP_200_OK)

        except Exception as e:
            status_code = status.HTTP_400_BAD_REQUEST
            response = {
                "error": {
                    "errorCode": 616,
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "errorMessage": str(e)
                },
                "response": None
            }
            return Response(response, status=status_code)


class ProviderRequestFetch(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            provider = User.objects.filter(
                Q(id=user['user_id']) & Q(userType=2)).first()
            if provider is None:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "provider user not found!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            latestTwo = RequestAssign.objects.filter(
                Q(providerId=provider) & Q(assignStatus__in=[1, 2])).order_by('-id')[:2]
            providerData = RequestAssign.objects.filter(
                Q(providerId=provider) & Q(assignStatus__in=[1, 2])).order_by('-id')
            # consult = RequestAssign.objects.filter(
            #     Q(providerId=provider) & Q(assignStatus__in=[1, 2])).first()
            # print(consult)
            # note = ProviderProgressNote.objects.filter(
            #     Q(consultantiontId__providerId=provider)).all().order_by('-id')
            # print(note)
            # userCheck = PatientUserAdditionalData.objects.filter(
            #     userId=consult.consultantiontId.userId.id).first()
            # print(userCheck.shareMedicalRecord)
            # if userCheck.shareMedicalRecord:
            #     progress = ProviderPrgressNoteSerailizer(note, many=True).data
            # else:
            #     progress = None
            if not latestTwo:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Not assigned data available"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            data = RequestAssignSerializer(providerData, many=True)
            data2 = RequestAssignSerializer(latestTwo, many=True)
            response = {
                "error": None,
                "response": {
                    "latestPatient": data2.data,
                    "patientDetails": data.data,
                    # "progresNoteDetails": progress,
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Requests available"
                    }
                }
            }
            return Response(response, status=status.HTTP_200_OK)

        except Exception as e:
            status_code = status.HTTP_400_BAD_REQUEST
            response = {
                "error": {
                    "errorCode": 616,
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "errorMessage": str(e)
                },
                "response": None
            }
            return Response(response, status=status_code)

class ProviderRequestFetchDetail(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            consultationId = pythonData.get('consultationId', False)
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            provider = User.objects.filter(
                Q(id=user['user_id']) & Q(userType=2)).first()
            if provider is None:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "provider user not found!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if not consultationId:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "consultationId field required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            consult = Consultantion.objects.filter(Q(id=consultationId) & Q(consultantionStatus__in=[1,2])).first()
            if not consult:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Invalid consultationId please check!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            note = ProviderProgressNote.objects.filter(
                Q(consultantiontId__providerId=provider) & Q(consultantiontId__userId=consult.userId.id)).all().order_by('-id')
            userCheck = PatientUserAdditionalData.objects.filter(
                userId=consult.userId.id).first()
            if userCheck.shareMedicalRecord:
                progress = ProviderPrgressNoteSerailizer(note, many=True).data
            else:
                progress = None
            
            patient = User.objects.filter(id=consult.userId.id).first()
            response = {
                "error": None,
                "response": {
                    "consultationStatus":consult.consultantionStatus,
                    "profileDetail":ProfileDetailSerializer(patient).data,
                    "progresNoteDetails": progress,
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Requests available"
                    }
                }
            }
            return Response(response, status=status.HTTP_200_OK)

        except Exception as e:
            status_code = status.HTTP_400_BAD_REQUEST
            response = {
                "error": {
                    "errorCode": 616,
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "errorMessage": str(e)
                },
                "response": None
            }
            return Response(response, status=status_code)

class RequestStatusChange(UpdateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            statuss = pythonData.get('status', False)
            consultationId = pythonData.get('consultationId', False)
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            provider = User.objects.filter(
                Q(id=user['user_id']) & Q(userType=2)).first()
            if provider is None:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "provider user not found!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            if statuss is None:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "status field required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            if consultationId is None:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "consultationId field required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            if statuss != 2 and statuss != 3:
                response = {
                    "error": {
                        "errorCode": 406,
                        "statusCode": status.HTTP_406_NOT_ACCEPTABLE,
                        "errorMessage": "Invalid status value 2 for accept and 3 for reject!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_406_NOT_ACCEPTABLE)

            consultCheckForAlready = Consultantion.objects.filter(Q(consultantionStatus=2) & Q(providerId=provider)).all()
            consultCheck = Consultantion.objects.filter(
                Q(id=consultationId) & Q(consultantionStatus=1)).first()
            if not consultCheck:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Invalid consultationId!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if statuss == 2:
                if consultCheckForAlready:
                    response = {
                        "error": {
                            "errorCode": 504,
                            "statusCode": status.HTTP_406_NOT_ACCEPTABLE,
                            "errorMessage": "You can not accepted request because another consultation already running!"
                        },
                        "response": None
                    }
                    return Response(response, status=status.HTTP_406_NOT_ACCEPTABLE)
                RequestAssign.objects.filter(Q(consultantiontId=consultCheck) & Q(
                    providerId=provider)).update(assignStatus=2)
                requests = RequestAssign.objects.filter(
                    Q(consultantiontId=consultCheck) & Q(assignStatus=1)).all()
                deviceTokenAll = []
                title = "Resquest Accepted"
                message = "Resquest Accepted From Another Coach"
                for request in requests:
                    deviceTokenAll.append(request.providerId.deviceToken)
                    request.assignStatus = 3
                    request.save()
                data = {
                    "requestNotification": "requestNotification",
                    "title": title,
                    "message": message,
                    "consultationId": consultationId,
                    "acceptedRequest": True
                }
                if deviceTokenAll:
                    notification = send_notification(
                        title, message, deviceTokenAll, data)
                
                Consultantion.objects.filter(id=consultationId).update(
                    consultantionStatus=2, providerId=provider)
                con = Consultantion.objects.filter(id=consultationId).first()
                User.objects.filter(id=con.providerId.id).update(isAvailable=False)
   
                response = {
                    "error": None,
                    "response": {
                        "message": {
                            'success': True,
                            "successCode": 101,
                            "statusCode": status.HTTP_200_OK,
                            "successMessage": "Successfully Accepted"
                        }
                    }
                }
                return Response(response, status=status.HTTP_200_OK)
            else:
                RequestAssign.objects.filter(Q(consultantiontId=consultCheck) & Q(
                    providerId=provider)).update(assignStatus=7)
                requests = RequestAssign.objects.filter(
                    Q(consultantiontId=consultCheck) & Q(assignStatus__in=[1, 2])).all()
                if not requests:
                    Consultantion.objects.filter(
                        id=consultationId).update(consultantionStatus=3)
                response = {
                    "error": None,
                    "response": {
                        "message": {
                            'success': True,
                            "successCode": 101,
                            "statusCode": status.HTTP_200_OK,
                            "successMessage": "Request Rejected Successfully!"
                        }
                    }
                }
                return Response(response, status=status.HTTP_200_OK)

        except Exception as e:
            status_code = status.HTTP_400_BAD_REQUEST
            response = {
                "error": {
                    "errorCode": 616,
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "errorMessage": str(e)
                },
                "response": None
            }
            return Response(response, status=status_code)


class GetProviderAfterAcceptRequest(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            consultationId = pythonData.get('consultationId', False)
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            userId = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=userId['user_id']) & Q(userType=1)).first()
            if user is None:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "user not found!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            if consultationId is None:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "consultationId field required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            consultCheck = Consultantion.objects.filter(
                Q(id=consultationId) & Q(consultantionStatus=2)).first()

            if not consultCheck:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Invalid consultationId!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            provider = RequestAssign.objects.filter(
                Q(consultantiontId=consultCheck) & Q(assignStatus=2)).first()
            if provider is None:
                response = {
                    "isFound": False,
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Provider not found please wait and try again!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            providerId = provider.providerId
            acceptedProvider = User.objects.filter(id=providerId.id).first()
            addtional = ProviderUserAdditionalData.objects.filter(
                userId=acceptedProvider).first()
            data = ProviderAdditionalDataSerializer2(addtional)
            consultationCount = Consultantion.objects.filter(
                Q(providerId=consultCheck.providerId.id) & Q(consultantionStatus=4)).all().count()
            ratings = RatingAndReview.objects.filter(userId=user).all().order_by('-id')
            ratSerial = RatingAndReviewForDetailSerializer2(ratings, many=True)
            ratingsAverage= RatingAndReview.objects.filter(userId=user).aggregate(Avg('providerRating'))
            response = {
                "error": None,
                "response": {
                    "Data": {
                        "isFound": True,
                        "ProviderDetail": data.data,
                        "consultationCount": consultationCount,
                        "ratingReviews":ratSerial.data,
                        "averageRating":ratingsAverage["providerRating__avg"]
                    },
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Congrats! Provider Found Successfully!"
                    }
                }
            }
            return Response(response, status=status.HTTP_200_OK)

        except Exception as e:
            status_code = status.HTTP_400_BAD_REQUEST
            response = {
                "error": {
                    "errorCode": 616,
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "errorMessage": str(e)
                },
                "response": None
            }
            return Response(response, status=status_code)


class RejectAfterTimeout(UpdateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            consultationId = pythonData.get('consultationId', False)
            title = pythonData.get('title', False)
            message = pythonData.get('message', False)
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            userId = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=userId['user_id'])).first()
            if user is None:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "user not found!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if consultationId is None:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "consultationId field required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if not Consultantion.objects.filter(Q(id=consultationId) & Q(consultantionStatus__in=[1, 2])).first():
                response = {
                    "error": {
                        "errorCode": 505,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Invalid consultation!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if not title or not message:
                response = {
                    "error": {
                        "errorCode": 506,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "title and message is required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            if Consultantion.objects.filter(Q(id=consultationId) & Q(consultantionStatus=1)).first():
                consultCheck = Consultantion.objects.filter(
                    Q(id=consultationId) & Q(consultantionStatus=1)).first()

                if not consultCheck:
                    response = {
                        "error": {
                            "errorCode": 503,
                            "statusCode": status.HTTP_404_NOT_FOUND,
                            "errorMessage": "Invalid consultationId!"
                        },
                        "response": None
                    }
                    return Response(response, status=status.HTTP_404_NOT_FOUND)

                requests = RequestAssign.objects.filter(
                    Q(consultantiontId=consultCheck) & Q(assignStatus=1)).all()
                if not requests:
                    response = {
                        "error": {
                            "errorCode": 504,
                            "statusCode": status.HTTP_404_NOT_FOUND,
                            "errorMessage": "Requests Not Available!"
                        },
                        "response": None
                    }
                    return Response(response, status=status.HTTP_404_NOT_FOUND)
                deviceTokenAll = []
                for request in requests:
                    deviceTokenAll.append(request.providerId.deviceToken)
                    request.assignStatus = 5
                    request.save()
                data = {
                    "requestNotification": "requestNotification",
                    "title": title,
                    "message": message,
                    "consultationId": consultationId,
                    "isMissedCall": "isMissedCall"
                }
                notification = send_notification(
                    title, message, deviceTokenAll, data)
                Consultantion.objects.filter(id=consultationId).update(
                    consultantionStatus=5)
                response = {
                    "error": None,
                    "response": {
                        "message": {
                            'success': True,
                            "successCode": 101,
                            "statusCode": status.HTTP_200_OK,
                            "successMessage": "Consultation failed!"
                        }
                    }
                }
                return Response(response, status=status.HTTP_200_OK)

            if Consultantion.objects.filter(Q(id=consultationId) & Q(consultantionStatus=2)).first():
                consultCheck = Consultantion.objects.filter(
                    Q(id=consultationId) & Q(consultantionStatus=2)).first()
                if not consultCheck:
                    response = {
                        "error": {
                            "errorCode": 503,
                            "statusCode": status.HTTP_404_NOT_FOUND,
                            "errorMessage": "Invalid consultationId!"
                        },
                        "response": None
                    }
                    return Response(response, status=status.HTTP_404_NOT_FOUND)

                requests = RequestAssign.objects.filter(
                    Q(consultantiontId=consultCheck) & Q(assignStatus=2)).all()
                if not requests:
                    response = {
                        "error": {
                            "errorCode": 504,
                            "statusCode": status.HTTP_404_NOT_FOUND,
                            "errorMessage": "Requests Not Available!"
                        },
                        "response": None
                    }
                    return Response(response, status=status.HTTP_404_NOT_FOUND)
                consult = Consultantion.objects.filter(
                    Q(id=consultationId) & Q(consultantionStatus=2)).first()
                if consult.userId.id == user.id:
                    requestingUser = consult.userId
                    requestingToUser = consult.providerId
                else:
                    requestingUser = consult.providerId
                    requestingToUser = consult.userId

                for request in requests:
                    request.assignStatus = 6
                    request.save()
                Consultantion.objects.filter(id=consultationId).update(
                    consultantionStatus=6)
                consultt = Consultantion.objects.filter(id=consultationId).first()
                User.objects.filter(id=consultt.providerId.id).update(isAvailable=True)
                if title and message:
                    uuser = User.objects.filter(id=requestingToUser.id).first()
                    deviceTokens = [uuser.deviceToken]
                    data = {
                        "requestNotification": "requestNotification",
                        "title": title,
                        "message": message,
                        "consultationId": consultationId,
                        "isMissedCall": "isMissedCall"
                    }
                    notification = send_notification(
                        title, message, deviceTokens, data)
                    response = {
                        "error": None,
                        "response": {
                            "message": {
                                'success': True,
                                "successCode": 101,
                                "statusCode": status.HTTP_200_OK,
                                "successMessage": "Consultation cancelled successfully!"
                            }
                        }
                    }
                    return Response(response, status=status.HTTP_200_OK)

                response = {
                    "error": None,
                    "response": {
                        "message": {
                            'success': True,
                            "successCode": 101,
                            "statusCode": status.HTTP_200_OK,
                            "successMessage": "Consultation cancelled successfully!"
                        }
                    }
                }
                return Response(response, status=status.HTTP_200_OK)

        except Exception as e:
            status_code = status.HTTP_400_BAD_REQUEST
            response = {
                "error": {
                    "errorCode": 616,
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "errorMessage": str(e)
                },
                "response": None
            }
            return Response(response, status=status_code)


class TwilioAccessTokenView(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            consultationId = pythonData.get('consultationId', False)
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            userId = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=userId['user_id'])).first()

            if user is None:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "user not found!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if not consultationId:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "ConsultationId required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            consult = Consultantion.objects.filter(
                Q(id=consultationId) & Q(consultantionStatus=2)).first()
            if not consult:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Invalid ConsultationId!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if consult.userId.id == user.id:
                requestingUser = consult.userId
                requestingToUser = consult.providerId
            else:
                requestingUser = consult.providerId
                requestingToUser = consult.userId
            ident = str(uuid.uuid4())[:8]+str(requestingUser.mobileNo)
            token = AccessToken(TWILIO_ACCOUNT_SID, TWILIO_API_KEY_SID,
                                TWILIO_API_KEY_SECRET, identity=requestingUser.mobileNo,
                                ttl=3600)
            token1 = AccessToken(TWILIO_ACCOUNT_SID, TWILIO_API_KEY_SID,
                                 TWILIO_API_KEY_SECRET, identity=requestingToUser.mobileNo,
                                 ttl=3600)
            token.add_grant(VideoGrant(room=ident))
            token1.add_grant(VideoGrant(room=ident))

            g_token = token.to_jwt()
            g_token1 = token1.to_jwt()
            #***********************PUSH NOTIFICATION***************************#
            uuser = User.objects.filter(id=requestingToUser.id).first()
            title = "Incomming call!!!"
            message = "Please join call as soon as possible!"
            deviceTokens = [uuser.deviceToken]
            data = {
                "twilioAccessTokenRequest": g_token.decode(),
                "roomId": ident,
                "title": "Incomming call!!!",
                "message": "Please join call as soon as possible!",
                "consultation": consult.id,
            }
            if uuser.deviceType == 1:
                notification = send_notification1(
                    deviceTokens, data)
            else:
                notification = send_notification(title, message,
                                                 deviceTokens, data)

            if notification:
                if uuser.userType == 1:
                    noti_for = 2
                else:
                    noti_for = 3
                Notifications.objects.create(
                    notificationType=2, title=title, message=message, notificationFor=noti_for, userId=uuser)
            #***********************PUSH NOTIFICATION***************************#
            # print("$$$$$$$$$$$$$$$$", consult.providerId.isAvailable)
            User.objects.filter(id=consult.providerId.id).update(isAvailable=False)
            response = {
                "error": None,
                "response": {
                    "twilioAccessTokenRequestTo": g_token1.decode(),
                    "roomId": ident,
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Twilio Room Generated SuccessFully"
                    }
                }
            }
            return Response(response, status=status.HTTP_200_OK)

        except Exception as e:
            status_code = status.HTTP_400_BAD_REQUEST
            response = {
                "error": {
                    "errorCode": 616,
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "errorMessage": str(e)
                },
                "response": None
            }
            return Response(response, status=status_code)


class ConsultationSessionsHistory(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            userId = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=userId['user_id']) & Q(userType=1)).first()

            if user is None:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "user not found!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            consultation = Consultantion.objects.filter(
                Q(userId=user) & Q(consultantionStatus=4)).all().order_by("-id")
            serializr = ConsultationDetailSessionHistorySerializer(
                consultation, many=True)
            response = {
                "error": None,
                "response": {
                    "consultationListWithProviders": serializr.data,
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Sessions History list"
                    }
                }
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            status_code = status.HTTP_400_BAD_REQUEST
            response = {
                "error": {
                    "errorCode": 616,
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "errorMessage": str(e)
                },
                "response": None
            }
            return Response(response, status=status_code)


class ConsultationSessionsHistoryDetail(RetrieveAPIView): 
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            providerId = pythonData.get('providerId', False)
            consultationId = pythonData.get('consultationId', False)
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            userId = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=userId['user_id']) & Q(userType=1)).first()

            if user is None:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "user not found!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            if not providerId:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "providerId field required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            if not consultationId:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "consultationId field required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            consultation = Consultantion.objects.filter(Q(userId=user) & Q(
                consultantionStatus=4) & Q(providerId=providerId) & Q(id=consultationId)).first()
            if not consultation:
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Invalid consultationId!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            user1 = User.objects.filter(id=consultation.providerId.id).first()
            additional = ProviderUserAdditionalData.objects.filter(
                userId=user1).first()
            trans = Transaction.objects.filter(
                consultantiontId=consultation).first()
            if not trans:
                response = {
                    "error": {
                        "errorCode": 505,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Transaction not happend!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            note = ProviderProgressNote.objects.filter(
                consultantiontId=consultation).first()
            if FavouriteProvider.objects.filter(Q(userId=user) & Q(providerId=user1)).first():
                isFavourite = True
            else:
                isFavourite = False

            ratings= RatingAndReview.objects.filter(providerId=consultation.providerId.id).order_by('-id')
            jsonData = RatingAndReviewForDetailSerializer2(ratings, many=True)
            rating = RatingAndReview.objects.filter(
                Q(consultationId=consultation)).first()
            if rating:
                ratData = {
                    "providerRating":rating.providerRating,
                    "feedbackComment":rating.feedbackComment
                }
            else:
                ratData = {
                    "providerRating":None,
                    "feedbackComment":None
                }

            data = {
                "consultationId": {
                    "id": consultation.id,
                    "consultationTime": consultation.createdAt,
                    "consultationFee": consultation.consultantiontFee,
                    "callDuration": trans.callDuration,
                    "createdAt":consultation.createdAt
                },
                "providerId": ProfileDetailSerializer(user1).data,
                "additional": ProviderAdditionalDataSerializer3(additional).data,
                "progressNote": ProviderPrgressNoteSerailizer(note).data,
                "isFavourite": isFavourite,
                "providerConsultationCount": Consultantion.objects.filter(Q(
                    consultantionStatus=4) & Q(providerId=providerId)).all().count(),
                "transactionDetails":{
                    "stripeFee":trans.stripeFee,
                    "adminCharge":trans.adminCharge,
                    "netAmmount":trans.netAmmount,
                    "reciept":trans.reciept
                },
                "ratingDetails": jsonData.data,
                "cuurentRating": ratData
            }
            response = {
                "error": None,
                "response": {
                    "consultationDetails": data,
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "consultation details fetched successfully!"
                    }
                }
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            status_code = status.HTTP_400_BAD_REQUEST
            response = {
                "error": {
                    "errorCode": 616,
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "errorMessage": str(e)
                },
                "response": None
            }
            return Response(response, status=status_code)


class ConsultationSessionsHistoryProvider(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            userId = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=userId['user_id']) & Q(userType=2)).first()

            if user is None:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "user not found!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            consultation = Consultantion.objects.filter(
                Q(providerId=user) & Q(consultantionStatus__in=[4,2])).all().order_by("-id")
            if not consultation:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "consultation not found!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            latestTwo = Consultantion.objects.filter(
                Q(providerId=user) & Q(consultantionStatus__in=[4,2])).all().order_by('-id')[:2]
            serializr = ConsultationDetailSessionHistorProviderySerializer(
                consultation, many=True)
            serializr1 = ConsultationDetailSessionHistorProviderySerializer(
                latestTwo, many=True)
            response = {
                "error": None,
                "response": {
                    "latestTwoConsultationData": serializr1.data,
                    "consultationListWithProviders": serializr.data,
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Sessions History list"
                    }
                }
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            status_code = status.HTTP_400_BAD_REQUEST
            response = {
                "error": {
                    "errorCode": 616,
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "errorMessage": str(e)
                },
                "response": None
            }
            return Response(response, status=status_code)


class ConsultationSessionsHistoryProviderDetail(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            userId = pythonData.get('userId', False)
            consultationId = pythonData.get('consultationId', False)
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            userr = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=userr['user_id']) & Q(userType=2)).first()
            if user is None:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "user not found!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            if not userId:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "userId field required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            if not consultationId:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "consultationId field required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            # userr = User.objects.filter(id=userId).first()
            # print(userr)
            consultation = Consultantion.objects.filter(Q(providerId=user) & Q(
                consultantionStatus=4) & Q(userId=userId) & Q(id=consultationId)).first()
            if not consultation:
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Invalid consultationId!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            user1 = User.objects.filter(id=consultation.userId.id).first()
            trans = Transaction.objects.filter(
                consultantiontId=consultation).first()
            if not trans:
                response = {
                    "error": {
                        "errorCode": 505,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Transaction not happend!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            prgressnote = ProviderProgressNote.objects.filter(
                consultantiontId=consultation).first()
            rating = RatingAndReview.objects.filter(
                Q(consultationId=consultation)).first()

            data = {
                "consultationId": {
                    "id": consultation.id,
                    "consultationTime": consultation.createdAt,
                    "consultationFee": consultation.consultantiontFee,
                    "callDuration": trans.callDuration,
                    "createdAt":consultation.createdAt
                },
                "userId": ProfileDetailSerializer(user1).data,
                "ratingDetails": RatingAndReviewForDetailSerializer(rating).data,
                "progressNoteDetails":ProviderPrgressNoteSerailizer(prgressnote).data,
                "transactionDetails":{
                    "stripeFee":trans.stripeFee,
                    "adminCharge":trans.adminCharge,
                    "netAmmount":trans.netAmmount,
                    "reciept":trans.reciept
                }
            }
            response = {
                "error": None,
                "response": {
                    "consultationDetails": data,
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "consultation details fetched successfully!"
                    }
                }
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            status_code = status.HTTP_400_BAD_REQUEST
            response = {
                "error": {
                    "errorCode": 616,
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "errorMessage": str(e)
                },
                "response": None
            }
            return Response(response, status=status_code)


class AddCallDuration(RetrieveAPIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            consultationId = pythonData.get('consultationId', False)
            callDuration = int(pythonData.get('callDuration', False))
            if not consultationId or not callDuration:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_406_NOT_ACCEPTABLE,
                        "errorMessage": "Required parameters is missing(Required parameters:callDuration,consultationId)"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_406_NOT_ACCEPTABLE)

            consult = Consultantion.objects.filter(Q(id=consultationId) & Q(consultantionStatus=2) & Q(paymentStatus=1)).first()
            if not consult:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Invalid consultation"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            consult.callDuration = callDuration
            consult.save()

            response = {
                "error": None,
                "response": {
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Call duration added successfully!"
                    }
                }
            }
            return Response(response, status=status.HTTP_200_OK)

        except Exception as e:
            status_code = status.HTTP_400_BAD_REQUEST
            response = {
                "error": {
                    "errorCode": 616,
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "errorMessage": str(e)
                },
                "response": None
            }
            return Response(response, status=status_code)