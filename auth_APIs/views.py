from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import JSONParser
import io
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from auth_APIs.models import User, licenseType, ProviderUserAdditionalData, ProviderUserLicenseDocs, PatientUserAdditionalData, ProviderStripeAccount
from .serializers import UserRegistrationSerializer, LicenseTypeSerializer, ProfileDetailSerializer, LisenceDocsSerializer, ProviderAdditionalDataSerializer, PatientAdditionalDataSerializer
import pgeocode
import math
from django.db.models import Q
from django.contrib.auth.models import update_last_login
from django.contrib.auth.hashers import make_password
import jwt
from sotto_admin_apis.settings import SECRET_KEY, STRIPE_API_KEY, BASE_URL
import stripe
from searchAPIs.models import Consultantion
from Helpers.helper import feeAndPriceSetting


class UserRegistrationView(CreateAPIView):
    UserRegistrationSerializer = UserRegistrationSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            userType = pythonData.get('userType', False)
            deviceType = pythonData.get('deviceType', False)
            email = pythonData.get('email', False)
            mobileNo = pythonData.get('mobileNo', False)
            password = pythonData.get('password', False)
            zipCode = pythonData.get('zipCode')
            experience = pythonData.get('experience', False)
            # licenseTypeId = pythonData.get('licenseTypeId', False)
            # licenseDocs = pythonData.get('licenseDocs', False)
            countryCode = pythonData.get('countryCode', False)
            userCheck = User.objects.filter(
                Q(email=email) | Q(mobileNo=mobileNo)).first()
            if userCheck:
                response = {
                    "error": {
                        "errorCode": 500,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "User email/mobile number already registered"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            if not userType:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "User type field is required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            if not email:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "Email field is required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            if not mobileNo:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "mobileNo field is required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            if not password:
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "password field is required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            if not countryCode:
                response = {
                    "error": {
                        "errorCode": 509,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "countryCode field is required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            if userType != 1 and userType != 2:

                response = {
                    "error": {
                        "errorCode": 505,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "Invalid userType"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            if deviceType != 1 and deviceType != 2:

                response = {
                    "error": {
                        "errorCode": 505,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "Invalid deviceType"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            if not zipCode:
                response = {
                    "error": {
                        "errorCode": 506,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "Zip code field is required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            # if userType == 2:
            #     if not licenseTypeId:
            #         response = {
            #             "error": {
            #                 "errorCode": 507,
            #                 "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
            #                 "errorMessage": "license type id is required!"
            #             },
            #             "response": None
            #         }
            #         return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            #     typeCheck = licenseType.objects.filter(
            #         id=licenseTypeId).first()
            #     if not typeCheck:
            #         response = {
            #             "error": {
            #                 "errorCode": 507,
            #                 "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
            #                 "errorMessage": "Invalid type id"
            #             },
            #             "response": None
            #         }
            #         return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            pythonData["fullName"] = str(
                pythonData["firstName"]+" "+pythonData["lastName"])

            nomi = pgeocode.Nominatim('us')
            resData = nomi.query_postal_code(zipCode)
            if math.isnan(resData.latitude):
                response = {
                    "error": {
                        "errorCode": 505,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "Invalid zip code!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            pythonData["lat"] = resData.latitude
            pythonData['lng'] = resData.longitude
            pythonData['state'] = resData.state_name
            if userType == 1:
                response = stripe.Customer.create(
                    email=email,
                    name=pythonData["fullName"],
                    metadata={
                        "name": pythonData['firstName'],
                        "mobileNo": pythonData['mobileNo'],
                        "zipCode": pythonData['zipCode']
                    }
                )
                pythonData['stripeCustomerId'] = response['id']
            else:
                pythonData['stripeCustomerId'] = None
            serializer = UserRegistrationSerializer(data=pythonData)
            if serializer.is_valid(raise_exception=True):
                user = serializer.save()
                if user is not None:
                    providerSett = feeAndPriceSetting()
                    if user.userType == 2:

                        # licenseTyp = licenseType.objects.filter(
                        #     id=licenseTypeId).first()
                        ProviderUserAdditionalData.objects.create(
                            experience=experience, userId=user, fee=providerSett.fee)
                        # for doc in licenseDocs:
                        #     ProviderUserLicenseDocs.objects.create(
                        #         userId=user, providerUserDocUrl=doc)
                    if user.userType == 1:
                        PatientUserAdditionalData.objects.create(
                            userId=user, minPrice=providerSett.minPrice, maxPrice=providerSett.maxPrice)
                    refresh = RefreshToken.for_user(user)
                    data = {
                        "userId": user.id,
                        "firstName": user.firstName,
                        "lastName": user.lastName,
                        "mobileNo": user.mobileNo,
                        "email": user.email,
                        "userType": user.userType,
                        "isVerified": user.isVerified,
                        "countryCode": user.countryCode,
                        "gender": user.genderType,
                        "token": str(RefreshToken.for_user(user).access_token),
                        "refreshToken": str(refresh),
                    }
                    response = {
                        "error": None,
                        "response": {
                            "data": data,
                            "message": {
                                'success': True,
                                "successCode": 101,
                                "statusCode": status.HTTP_200_OK,
                                "successMessage": "User registered successfully."
                            }
                        }
                    }
                    return Response(response, status=status.HTTP_200_OK)
                else:
                    response = {
                        "error": {
                            "errorCode": 502,
                            "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                            "errorMessage": "Error while registring user. Please try again later."
                        },
                        "response": None
                    }
                return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
                        "errorMessage": "Error while registring user. Please try again later."
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as exception:
            response = {
                "error": {
                    "errorCode": 504,
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "errorMessage": str(exception)
                },
                "response": None
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class GetAllLicenseType(RetrieveAPIView):

    permission_classes = (AllowAny,)

    def get(self, request):
        try:
            licenseTypes = licenseType.objects.all()
            data = LicenseTypeSerializer(data=licenseTypes, many=True)
            data.is_valid()
            # balance = stripe.Balance.retrieve(
            #     stripe_account="acct_1LGHOJL9hQM0WGfv"
            # )
            # print(balance["available"])
            # usdoller = balance["available"]["amount"]/100
            # deleteStripeAccount("acct_1LbJ83Q5wy1kjerS")
            response = {
                "error": None,
                "response": {
                    "data": {
                        "licenseTypes": data.data
                        # "Balance":balance
                    },
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "All LicenseTypes"
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


class UserLoginView(RetrieveAPIView):

    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            email_mobileNo = pythonData.get(
                'mobileNo', False)
            userType = pythonData.get('userType', False)
            deviceType = pythonData.get('deviceType', False)
            password = pythonData.get('password', False)
            deviceToken = pythonData.get('deviceToken', False)

            if not userType:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "User type field is required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            if not email_mobileNo:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "Please enter email / mobileNo / User ID and password to login!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            if not password:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "Please enter password to login!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            if userType != 1 and userType != 2:
                response = {
                    "error": {
                        "errorCode": 505,
                        "statusCode": status.HTTP_401_UNAUTHORIZED,
                        "errorMessage": "Cross application login is prohibited!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_401_UNAUTHORIZED)

            if not deviceType:
                response = {
                    "error": {
                        "errorCode": 512,
                        "statusCode": status.HTTP_401_UNAUTHORIZED,
                        "errorMessage": "device Type field required"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_401_UNAUTHORIZED)
            user = User.objects.filter(
                Q(mobileNo=email_mobileNo) & Q(userType=userType)).first()
            if user is None:
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "User not found!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            if not user.check_password(request.data['password']):
                response = {
                    "error": {
                        "errorCode": 506,
                        "statusCode": status.HTTP_401_UNAUTHORIZED,
                        "errorMessage": "Please enter correct email/mobileNo and password to login!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_401_UNAUTHORIZED)

            if user.isDeleted == 1:
                response = {
                    "error": {
                        "errorCode": 507,
                        "statusCode": status.HTTP_401_UNAUTHORIZED,
                        "errorMessage": "Your account has been deleted. Please contact to admin for further assistance!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_401_UNAUTHORIZED)

            if user.isActive == 0:
                response = {
                    "error": {
                        "errorCode": 508,
                        "statusCode": status.HTTP_401_UNAUTHORIZED,
                        "errorMessage": "Your account is rejected by admin, please contact to admin for futher assistance!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_401_UNAUTHORIZED)
            if user.userType == 2:
                # if user.isApproved == 1:
                #     response = {
                #         "error": {
                #             "errorCode": 509,
                #             "statusCode": status.HTTP_401_UNAUTHORIZED,
                #             "errorMessage": "Your account is not approved. Please wait till complete verification. And try again later."
                #         },
                #         "response": None
                #     }
                #     return Response(response, status=status.HTTP_401_UNAUTHORIZED)

                if user.isApproved == 3:
                    response = {
                        "error": {
                            "errorCode": 510,
                            "statusCode": status.HTTP_401_UNAUTHORIZED,
                            "errorMessage": "Your account is disapproved. Please contact to admin for futher assistance!"
                        },
                        "response": None
                    }
                    return Response(response, status=status.HTTP_401_UNAUTHORIZED)
            update_last_login(None, user)
            if deviceToken:
                User.objects.filter(id=user.id).update(
                    deviceToken=deviceToken)

            User.objects.filter(id=user.id).update(
                deviceType=deviceType)

            refresh = RefreshToken.for_user(user)
            data = {
                "userId": user.id,
                "profileImage": user.profileImage,
                "firstName": user.firstName,
                "lastName": user.lastName,
                "mobileNo": user.mobileNo,
                "userType": user.userType,
                "email": user.email,
                "isVerified": user.isVerified,
                "isAvailable": user.isAvailable,
                # "stripeCustomerId": user.stripeCustomerId,
                "token": str(refresh.access_token),
                "refreshToken": str(refresh),
            }

            response = {
                "error": None,
                "response": {
                    "data": data,
                    "message": {
                        'success': True,
                        "successCode": 102,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Logged in successfylly."
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


class ForgetPasswordUpdate(UpdateAPIView):

    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            mobileNo = pythonData.get(
                'mobileNo', False)
            newPassword = pythonData.get('newPassword', False)
            if not mobileNo:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "Mobile no field is required"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            if not newPassword:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "New password field required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            user = User.objects.filter(
                Q(mobileNo=mobileNo)).first()
            if user is None:
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "User not found!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            if user.userType == 3:
                response = {
                    "error": {
                        "errorCode": 505,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "This this admin user you can't change password"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            user.password = make_password(newPassword)
            user.save()

            response = {
                "error": None,
                "response": {
                    "message": {
                        'success': True,
                        "successCode": 102,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Password changed successfully."
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


class ProfileDetail(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(id=user['user_id']).first()
            if user is None:
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "User not found!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if user.userType == 1:
                data = ProfileDetailSerializer(user)
                additional = PatientUserAdditionalData.objects.filter(
                    userId=user).first()
                response = {
                    "error": None,
                    "response": {
                        "data": {
                            "UserDetails": data.data,
                            "minPrice": additional.minPrice,
                            "maxPrice": additional.maxPrice,
                            "shareMedicalRecord": additional.shareMedicalRecord
                        },
                        "message": {
                            'success': True,
                            "successCode": 101,
                            "statusCode": status.HTTP_200_OK,
                            "successMessage": "User Details"
                        }
                    }
                }
                return Response(response, status=status.HTTP_200_OK)
            else:
                addtionalData = ProviderUserAdditionalData.objects.filter(
                    userId=user.id).first()
                # docImages = ProviderUserLicenseDocs.objects.filter(
                #     userId=user.id).all()
                consultationCount = Consultantion.objects.filter(
                    Q(providerId=user) & Q(consultantionStatus=4)).all().count()
                # docData = LisenceDocsSerializer(data=docImages, many=True)
                # docData.is_valid()
                data = {
                    "id": user.id,
                    "firstName": user.firstName,
                    "lastName": user.lastName,
                    "email": user.email,
                    "mobileNo": user.mobileNo,
                    "profileImage": user.profileImage,
                    "userType": user.userType,
                    "genderType": user.genderType,
                    "dateOfBirth": user.dateOfBirth,
                    "zipCode": user.zipCode,
                    "experience": addtionalData.experience,
                    "fee": addtionalData.fee,
                    "about": addtionalData.about,
                    # "licenseDocs": docData.data,
                    "consultationCount": consultationCount
                }
                # res = stripe.Account.create(
                #     type="express",
                #     country="US",
                #     email="monty2@yopmail.com",
                #     capabilities={
                #         "card_payments": {"requested": True},
                #         "transfers": {"requested": True},
                #     },
                # )

                # print(res["id"])
                # print(res)
                # res2 = stripe.AccountLink.create(
                #     account=res["id"],
                #     refresh_url="https://example.com/reauth",
                #     return_url="https://example.com/return",
                #     type="account_onboarding",
                # )
                # print(res2)
                response = {
                    "error": None,
                    "response": {
                        "data": {
                            "UserDetails": data
                        },
                        "message": {
                            'success': True,
                            "successCode": 101,
                            "statusCode": status.HTTP_200_OK,
                            "successMessage": "User Details"
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


class PasswordVerification(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(id=user['user_id']).first()
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            password = pythonData.get('password', False)

            if user is None:
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "User not found!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            if not password:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "Please enter password to login!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            if not user.check_password(password):
                response = {
                    "error": {
                        "errorCode": 506,
                        "statusCode": status.HTTP_401_UNAUTHORIZED,
                        "errorMessage": "Wrong Password! Unauthorized User"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_401_UNAUTHORIZED)

            response = {
                "error": None,
                "response": {
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Valid password"
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


class UpdateMobileNo(UpdateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            token = request.META.get(
                'HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(id=user['user_id']).first()
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            newMobileNo = pythonData.get('newMobileNo', False)

            if user is None:
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "User not found!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            if not newMobileNo:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "New mobileNo is required"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            if int(user.mobileNo) == int(newMobileNo):
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "This is your old mobileNo can't update"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            user.mobileNo = newMobileNo
            user.save()

            response = {
                "error": None,
                "response": {
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Mobile number update successfully"
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


class UpdateUserProfile(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    UserRegistrationSerializer = UserRegistrationSerializer

    def put(self, request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(id=user['user_id']).first()
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            zipCode = pythonData.get('zipCode', False)
            # minPrice = pythonData.get('minPrice', False)
            # maxPrice = pythonData.get('maxPrice', False)
            shareMedicalRecord = pythonData.get('shareMedicalRecord', False)
            if user is None:
                response = {
                    "error": {
                        "errorCode": 513,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "User not found with this user id."
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_200_OK)
            if zipCode:
                nomi = pgeocode.Nominatim('us')
                resData = nomi.query_postal_code(zipCode)
                if math.isnan(resData.latitude):
                    response = {
                        "error": {
                            "errorCode": 505,
                            "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                            "errorMessage": "Invalid zip code!"
                        },
                        "response": None
                    }
                    return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
                pythonData["lat"] = resData.latitude
                pythonData['lng'] = resData.longitude
                pythonData['state'] = resData.state_name
            if user.userType == 2:
                serializer = UserRegistrationSerializer(
                    user, data=pythonData, partial=True
                )
                addDataIns = ProviderUserAdditionalData.objects.filter(
                    userId=user.id).first()
                serializer1 = ProviderAdditionalDataSerializer(
                    addDataIns, data=pythonData, partial=True
                )
                if serializer1.is_valid(raise_exception=True) and serializer.is_valid(raise_exception=True):
                    serializer.save()
                    serializer1.save()
                    # licenseDocs = pythonData.get('licenseDocs', False)
                    # if licenseDocs:
                    #     for doc in licenseDocs:
                    #         ProviderUserLicenseDocs.objects.create(
                    #             userId=user, providerUserDocUrl=doc)
                    #     user.isApproved = 1
                    #     user.save()
                    response = {
                        "error": None,
                        "response": {
                            "message": {
                                'success': True,
                                "successCode": 103,
                                "statusCode": status.HTTP_200_OK,
                                "successMessage": "User profile updated successfully."
                            }
                        }
                    }
                    return Response(response, status=status.HTTP_200_OK)
            if user.userType == 1:
                # if minPrice or maxPrice:
                patient_additi = PatientUserAdditionalData.objects.filter(
                    userId=user).first()
                if patient_additi:
                    serializer1 = PatientAdditionalDataSerializer(
                        patient_additi, data=pythonData, partial=True
                    )
                    serializer1.is_valid(raise_exception=True)
                    serializer1.save()
                else:
                    PatientUserAdditionalData.objects.create(
                        userId=user, minPrice=pythonData['minPrice'], maxPrice=pythonData['maxPrice'])
            # pythonData["fullName"] = str(
            #     pythonData["firstName"]+" "+pythonData["lastName"])

            serializer = UserRegistrationSerializer(
                user, data=pythonData, partial=True
            )

            if serializer.is_valid(raise_exception=True):
                serializer.save()
                response = {
                    "error": None,
                    "response": {
                        "message": {
                            'success': True,
                            "successCode": 103,
                            "statusCode": status.HTTP_200_OK,
                            "successMessage": "User profile updated successfully."
                        }
                    }
                }
                return Response(response, status=status.HTTP_200_OK)
        except Exception as exception:
            response = {
                "error": {
                    "errorCode": 514,
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "errorMessage": str(exception)
                },
                "response": None
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class DeleteDoc(UpdateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(id=user['user_id']).first()
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            docId = pythonData.get('docId', False)
            if user is None:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "User not found with this user id."
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_200_OK)
            if docId is None:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "Document id is required"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_200_OK)

            doc = ProviderUserLicenseDocs.objects.filter(
                Q(id=docId) & Q(userId=user)).first()
            if not doc:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "Invalid doc id !"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_200_OK)
            docCount = ProviderUserLicenseDocs.objects.filter(
                userId=user.id).all().count()
            if docCount <= 1:
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "You can not delete last document please add more document images first!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_200_OK)

            ProviderUserLicenseDocs.objects.filter(
                Q(id=docId) & Q(userId=user)).delete()
            response = {
                "error": None,
                "response": {
                    "message": {
                        'success': True,
                        "successCode": 103,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Docdumet deleted successfully successfully."
                    }
                }
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as exception:
            response = {
                "error": {
                    "errorCode": 514,
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "errorMessage": str(exception)
                },
                "response": None
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class EmailOrMobileNoVerification(RetrieveAPIView):

    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            email = pythonData.get('email', False)
            mobileNo = pythonData.get('mobileNo', False)
            if not email and not mobileNo:
                response = {
                    "error": {
                        "errorCode": 500,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "Pass atleast one parameter"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            if email:
                userCheck = User.objects.filter(
                    Q(email=email)).first()
                if userCheck:
                    response = {
                        "error": {
                            "errorCode": 500,
                            "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                            "errorMessage": "User email already registered"
                        },
                        "response": None
                    }
                    return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            if mobileNo:
                userCheck1 = User.objects.filter(
                    Q(mobileNo=mobileNo)).first()
                if userCheck1:
                    response = {
                        "error": {
                            "errorCode": 500,
                            "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                            "errorMessage": "User mobileNo already registered"
                        },
                        "response": None
                    }
                    return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            response = {
                "error": None,
                "response": {
                    "message": {
                        'success': True,
                        "successCode": 101,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "This is taja taja user"
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


class VisibilityOnOff(UpdateAPIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=user['user_id']) & Q(userType=2)).first()
            if user is None:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "User not found!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            providerdata = ProviderUserAdditionalData.objects.filter(
                userId=user).first()
            if providerdata.fee == 0:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "Please update your consultation fee first!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            stripeCheck = ProviderStripeAccount.objects.filter(
                Q(userId=user) & Q(isCompleted=True)).first()
            if not stripeCheck:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "Add a payment method to turn on your visibilty!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if user.isAvailable == True:
                user.isAvailable = False
                user.save()
                response = {
                    "error": None,
                    "response": {
                        "isAvailable": user.isAvailable,
                        "userId": user.id,
                        "message": {
                            'success': True,
                            "successCode": 102,
                            "statusCode": status.HTTP_200_OK,
                            "successMessage": "Visibility Off Successfully"
                        }
                    }
                }
                return Response(response, status=status.HTTP_200_OK)
            else:
                user.isAvailable = True
                user.save()
                response = {
                    "error": None,
                    "response": {
                        "isAvailable": user.isAvailable,
                        "userId": user.id,
                        "message": {
                            'success': True,
                            "successCode": 102,
                            "statusCode": status.HTTP_200_OK,
                            "successMessage": "Visibility On Successfully"
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


class UserLogout(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            refreshToken = pythonData.get('refresh', False)
            if not refreshToken:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "Token is required to logout!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            user = jwt.decode(refreshToken, key=SECRET_KEY,
                              algorithms=['HS256', ])
            userr = User.objects.filter(
                Q(id=user['user_id'])).first()
            if userr is None:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "User not found invalid access token!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            RefreshToken(refreshToken).blacklist()
            userr.deviceToken = None
            userr.save()
            response = {
                "error": None,
                "response": {
                    "message": {
                        'success': True,
                        "successCode": 102,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Logout successfully."
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


class ChangePasswordView(UpdateAPIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
            user = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256', ])
            user = User.objects.filter(
                Q(id=user['user_id'])).first()
            if user is None:
                response = {
                    "error": {
                        "errorCode": 501,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "User not found!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            oldPassword = pythonData.get(
                'oldPassword', False)
            newPassword = pythonData.get('newPassword', False)
            if not oldPassword:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "oldPassword field is required"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            if not newPassword:
                response = {
                    "error": {
                        "errorCode": 503,
                        "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "errorMessage": "New password field required!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            if not user.check_password(oldPassword):
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_401_UNAUTHORIZED,
                        "errorMessage": "Please enter your correct old password!"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_401_UNAUTHORIZED)

            user.password = make_password(newPassword)
            user.save()

            response = {
                "error": None,
                "response": {
                    "message": {
                        'success': True,
                        "successCode": 102,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Password changed successfully."
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


class CreateProviderStripeAccount(CreateAPIView):
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
            stripeAccount = ProviderStripeAccount.objects.filter(
                userId=user).first()
            if stripeAccount:
                if not stripeAccount.isCompleted:

                    response = {
                        "error": None,
                        "response": {
                            "accountDetail": {
                                "instanceId": stripeAccount.id,
                                "stripeAccountId": stripeAccount.stipeAccountId,
                                "accountStatus": "incomplete"
                            },
                            "message": {
                                'success': True,
                                "successCode": 102,
                                "statusCode": status.HTTP_200_OK,
                                "successMessage": "Account already created please check details."
                            }
                        }
                    }
                    return Response(response, status=status.HTTP_200_OK)
                else:
                    if stripeAccount.isCompleted:
                        response = {
                            "error": {
                                "errorCode": 503,
                                "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                                "errorMessage": "Stripe account already exists"
                            },
                            "response": None
                        }
                        return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            stripeRes = stripe.Account.create(
                type="express",
                country="US",
                email=user.email,
                capabilities={
                        "card_payments": {"requested": True},
                        "transfers": {"requested": True},
                },
            )
            stripeAccountId = stripeRes["id"]
            accountRef = ProviderStripeAccount.objects.create(
                userId=user, stipeAccountId=stripeAccountId)
            response = {
                "error": None,
                "response": {
                    "accountDetail": {
                        "instanceId": accountRef.id,
                        "stripeAccountId": accountRef.stipeAccountId,
                        "providerId": user.id,
                        "accountStatus": "incomplete"
                    },
                    "message": {
                        'success': True,
                        "successCode": 102,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Account created successfully please link account now."
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


class LinkProviderStripeAccount(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            pythonData = JSONParser().parse(io.BytesIO(request.body))
            instanceId = pythonData.get('instanceId', False)
            # refreshUrl = pythonData.get('refreshUrl', False)
            # returnUrl = pythonData.get('returnUrl', False)
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
            if not instanceId:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "instanceId required"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            # if not refreshUrl or not returnUrl:
            #     response = {
            #         "error": {
            #             "errorCode": 503,
            #             "statusCode": status.HTTP_404_NOT_FOUND,
            #             "errorMessage": "refreshUrl and returnUrl are required"
            #         },
            #         "response": None
            #     }
            #     return Response(response, status=status.HTTP_404_NOT_FOUND)

            refreshLink = f"{BASE_URL}/refresh-page-view"
            returnLink = f"{BASE_URL}/return-page-view"
            stripeAccount = ProviderStripeAccount.objects.filter(
                Q(userId=user) & Q(id=instanceId) & Q(isCompleted=False)).first()
            if not stripeAccount:
                response = {
                    "error": {
                        "errorCode": 504,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "invalid account details please check"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            linkIns = stripe.AccountLink.create(
                account=stripeAccount.stipeAccountId,
                refresh_url=refreshLink,
                return_url=returnLink,
                type="account_onboarding",
            )
            response = {
                "error": None,
                "response": {
                    "accountOnboarding": linkIns,
                    "message": {
                        'success': True,
                        "successCode": 102,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Account link generated successfully Follow onboarding link!"
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


class ProviderStripeAccountStatusChange(UpdateAPIView):
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
            stripeAccount = ProviderStripeAccount.objects.filter(
                Q(userId=user) & Q(isCompleted=False)).first()
            if not stripeAccount:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "invalid account details please check"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            res1 = stripe.Account.retrieve(stripeAccount.stipeAccountId)
            error = res1["capabilities"]["transfers"]
            error2 = res1["capabilities"]["card_payments"]
            if error == "inactive" and error2 == "inactive":
                response = {
                    "errors": error,
                    "errorCode": 503,
                    "statusCode": status.HTTP_422_UNPROCESSABLE_ENTITY,
                    "errorMessage": "Your created account missing some required details please register again",
                    "response": None
                }
                return Response(response, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            loginLink = stripe.Account.create_login_link(
                stripeAccount.stipeAccountId)
            url = loginLink["url"]
            stripeAccount.isCompleted = True
            stripeAccount.loginLink = url
            stripeAccount.save()
            response = {
                "error": None,
                "response": {
                    "isCompleted": True,
                    "loginLink": url,
                    "message": {
                        'success': True,
                        "successCode": 102,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Stripe account completed successfully"
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


class ProviderStripeAccountCheck(UpdateAPIView):
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
            stripeAccount = ProviderStripeAccount.objects.filter(
                Q(userId=user) & Q(isCompleted=True)).first()
            if not stripeAccount:
                response = {
                    "error": {
                        "errorCode": 502,
                        "statusCode": status.HTTP_404_NOT_FOUND,
                        "errorMessage": "invalid account please check"
                    },
                    "response": None
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            if stripeAccount.isCompleted:
                isCompleted = True
                url = stripeAccount.loginLink
            else:
                isCompleted = False
                url = None
            response = {
                "error": None,
                "response": {
                    "isCompleted": isCompleted,
                    "loginLink": url,
                    "message": {
                        'success': True,
                        "successCode": 102,
                        "statusCode": status.HTTP_200_OK,
                        "successMessage": "Stripe account completed successfully"
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


def deleteStripeAccount(accountId):
    stripe.Account.delete(accountId)
    return True


# class ThanksAll(RetrieveAPIView):
#     permission_classes = (AllowAny,)

#     def get(self, request):
#         try:
#             data={
#                 0:"Apponward \u2764\uFE0F",
#                 1:"Aakash bhai \u2764\uFE0F",
#                 2:"Hinmanshu \u2764\uFE0F",
#                 3:"shivam bhai \u2764\uFE0F",
#                 4:"Sumit bhai \u2764\uFE0F",
#                 5:"Mayank bhai \u2764\uFE0F",
#                 6:"Ashok bhai \u2764\uFE0F",
#                 7:"Abhishek bhai \u2764\uFE0F",
#                 8:"Ayushi \u2764\uFE0F",
#                 9:"Shivanii pundir \u2764\uFE0F",
#                 10:"Shivani \u2764\uFE0F",
#                 11:"Anusha \u2764\uFE0F",
#                 12:"Aditya bhai \u2764\uFE0F",
#                 13:"Pankaj bhai \u2764\uFE0F",
#                 14:"Shilpi \u2764\uFE0F",
#                 15:"Anand Sir \u2764\uFE0F",
#                 16:"Jay \u2764\uFE0F"
#             }
#             response = {
#                 "Family": "Apponward",
#                 "response": {
#                     "Order_by":"FIFO",
#                     "Spacial_Thanks_to_all":data,
#                     "message": {
#                         'success': True,
#                         "date": "10 Sept",
#                         "statusCode": status.HTTP_200_OK,
#                         "successMessage": "Thanks to all for lovely wishes guys!!!!"
#                     }
#                 }
#             }
#             return Response(response, status=status.HTTP_200_OK)
#         except Exception as exception:
#             response = {
#                 "error": {
#                     "errorCode": 511,
#                     "statusCode": status.HTTP_400_BAD_REQUEST,
#                     "errorMessage": str(exception)
#                 },
#                 "response": None
#             }
#             return Response(response, status=status.HTTP_400_BAD_REQUEST)
