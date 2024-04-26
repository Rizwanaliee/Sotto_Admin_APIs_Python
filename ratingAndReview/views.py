from functools import partial
from rest_framework.generics import CreateAPIView, RetrieveAPIView, DestroyAPIView
import io
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import JSONParser
from auth_APIs.serializers import ProfileDetailSerializer
from sotto_admin_apis.settings import SECRET_KEY
import jwt
from .models import FavouriteProvider, RatingAndReview
from auth_APIs.models import User
from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from searchAPIs.models import Consultantion
from .serialzers import FavouriteProviderSerializer, RatingAndReviewSerializer, RatingAndReviewForDetailSerializer,RatingAndReviewForDetailSerializer2
from django.utils import timezone
import datetime
from django.db.models import Avg
from auth_APIs.serializers import ProfileDetailForTopRatedCoachesSerializer


# Create your views here.

class GetProviderDetailForFavourite(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            ConsultationId = pythonData.get('ConsultationId', False)
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
            if not ConsultationId:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "ConsultationId required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            consult = Consultantion.objects.filter(
                Q(id=ConsultationId) & Q(consultantionStatus__in=[2, 4])).first()
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
            provider = User.objects.filter(id=consult.providerId.id).first()
            if FavouriteProvider.objects.filter(Q(providerId=provider) & Q(userId=user)).first():
                isFavourite = True
            else:
                isFavourite = False
            data = {
                "providerId": provider.id,
                "fullName": provider.fullName,
                "profileImage": provider.profileImage,
                "isFavourite": isFavourite
            }

            response = {
                "error": None,
                "profileDetails": data,
                "response": {
                    "message": {
                        'success': True,
                        "successCode": 102,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Detail fetched successfully."
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


class MarkFavouriteProvider(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            providerId = pythonData.get('providerId', False)
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
            if not providerId:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "providerId required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if not User.objects.filter(Q(id=providerId) & Q(userType=2) & Q(isDeleted=False)).first():
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Invalid providerId!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            provider = User.objects.filter(Q(id=providerId) & Q(
                userType=2) & Q(isDeleted=False)).first()
            if FavouriteProvider.objects.filter(Q(providerId=provider) & Q(userId=user)).first():
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": f'{provider.fullName} already added in your favourite list!'
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            FavouriteProvider.objects.create(providerId=provider, userId=user)
            response = {
                "error": None,
                "response": {
                    "message": {
                        'success': True,
                        "successCode": 102,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": f'{provider.fullName} successfully added in your favourite list'
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


class RemoveFavouriteProvider(DestroyAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            providerId = pythonData.get('providerId', False)
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
            if not providerId:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "providerId required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if not User.objects.filter(Q(id=providerId) & Q(userType=2) & Q(isDeleted=False)).first():
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Invalid providerId!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            provider = User.objects.filter(Q(id=providerId) & Q(
                userType=2) & Q(isDeleted=False)).first()
            if not FavouriteProvider.objects.filter(Q(providerId=provider) & Q(userId=user)).first():
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": f'{provider.fullName} not in favourite list!'
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            FavouriteProvider.objects.filter(
                Q(providerId=provider) & Q(userId=user)).delete()
            response = {
                "error": None,
                "response": {
                    "message": {
                        'success': True,
                        "successCode": 102,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": f'{provider.fullName} successfully removed from favourite list!'
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


class FavouriteProviderList(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            # pythonData = JSONParser().parse(io.BytesIO(request.body))
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

            listFav = FavouriteProvider.objects.filter(userId=user).all()
            data = FavouriteProviderSerializer(data=listFav, many=True)
            data.is_valid()
            response = {
                "error": None,
                "response": {
                    "favouriteProviders": data.data,
                    "message": {
                        'success': True,
                        "successCode": 102,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Favourite providers list fetched successfully"
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


class RatingAndReviewView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=user['user_id']) & Q(userType=1)).first()
            rating = pythonData.get("providerRating", False)
            consultationId = pythonData.get("consultationId", False)
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
            if not rating or not consultationId:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Required parameters is missing(Required parameters:rating,consultationId)"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            consultCheck = Consultantion.objects.filter(Q(id=consultationId) & Q(consultantionStatus__in=[2,4])).first()  
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

            if rating > 5 or rating < 1:
                response = {
                    "error": {
                        "errorCode": 505,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "Rating number shoud be between 1 to 5"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            pythonData["userId"] = consultCheck.userId.id
            pythonData["providerId"] = consultCheck.providerId.id
            if not RatingAndReview.objects.filter(consultationId=consultCheck).first():
                serializer = RatingAndReviewSerializer(data=pythonData)
                if serializer.is_valid(raise_exception=True):
                    rating = serializer.save()
                    response = {
                        "error": None,
                        "response": {
                            "message": {
                                'success': True,
                                "successCode": 102,
                                "statusCode": status.HTTP_200_OK,
                                "successMessage": "Rating and reviews are submited successfully!"
                            }
                        }
                    }
                    return Response(response, status=status.HTTP_200_OK)
                else:
                    response = {
                        "error": {
                            "errorCode": 503,
                            "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                            "errorMessage": "Error while adding rating review. Please try again later."
                        },
                        "response": None
                    }
                    return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                response = {
                    "error": {
                        "errorCode": 505,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": f"Consultation id {consultCheck.id} already rated"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

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


class TopRatedProviders(RetrieveAPIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        try:
            now = timezone.now()
            one_month_ago = datetime.datetime(now.year, now.month - 1, 1)
            month_end = datetime.datetime(
                now.year, now.month, 1) - datetime.timedelta(seconds=1)
            consultations = Consultantion.objects.filter(Q(consultantionStatus=4) & Q(createdAt__gt=one_month_ago) & Q(createdAt__lt=month_end)).values_list('providerId',flat=True).distinct()
            if consultations:
                providers = RatingAndReview.objects.filter(providerId__in=consultations).order_by('-providerRating').values_list('providerId',flat=True).distinct()
                latest3Providers = RatingAndReview.objects.filter(providerId__in=consultations).order_by('-providerRating').values_list('providerId',flat=True).distinct()[:3]

                users = User.objects.filter(id__in=providers)
                latest3Users = User.objects.filter(id__in=latest3Providers)
                latest3 = ProfileDetailForTopRatedCoachesSerializer(latest3Users, many=True)
                jsonData =  ProfileDetailForTopRatedCoachesSerializer(users, many=True)
            else:
                consultations = Consultantion.objects.filter(Q(consultantionStatus=4)).values_list('providerId',flat=True).distinct()
                providers = RatingAndReview.objects.filter(providerId__in=consultations).order_by('-providerRating').values_list('providerId',flat=True).distinct()
                latest3Providers = RatingAndReview.objects.filter(providerId__in=consultations).order_by('-providerRating').values_list('providerId',flat=True).distinct()[:3]

                users = User.objects.filter(id__in=providers)
                latest3Users = User.objects.filter(id__in=latest3Providers)
                latest3 = ProfileDetailForTopRatedCoachesSerializer(latest3Users, many=True)
                jsonData =  ProfileDetailForTopRatedCoachesSerializer(users, many=True)

            response = {
                "error": None,
                "response": {
                    "latestThree":latest3.data,
                    "topRatedProviders":jsonData.data,
                    "message": {
                        'success': True,
                        "successCode": 102,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Top rated providers list fetched successfully"
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


class RatingAndReviewsWithAverageRate(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=user['user_id']) & Q(userType=2)).first()

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
            ratings= RatingAndReview.objects.filter(providerId=user).order_by('-id')
            ratingsAverage= RatingAndReview.objects.filter(providerId=user).aggregate(Avg('providerRating'))
            jsonData = RatingAndReviewForDetailSerializer2(ratings, many=True)

            response = {
                "error": None,
                "response": {
                    "ratingCount":ratings.count(),
                    "averageRating":ratingsAverage,
                    "sumitKiRating":ratingsAverage["providerRating__avg"],
                    "ratingAndReviews":jsonData.data,
                    "message": {
                        'success': True,
                        "successCode": 102,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Rate and review list fetched successfully"
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