from .serializers import *
from rest_framework import generics
from .models import *
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
import random

def otp_generator():
    otp = random.randint(100000, 999999)
    return str(otp)

class CustomerExistsOrNot(APIView):
    def get(self, request, phone_number):
        if LykaUser.objects.role_exists_phone(phone=phone_number, role=LykaUser.CUSTOMER):
            return Response({"message" : "Customer already exists with the same number"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message" : "Phone number is not used"}, status=status.HTTP_200_OK)
        
class PhoneLogin(APIView):
    def get(self, request):
        phone_number = request.data["phone"]
        password = request.data["password"]
        if LykaUser.objects.role_exists_phone(phone=phone_number, role=LykaUser.CUSTOMER):
            user = LykaUser.objects.get(phone=phone_number, role=LykaUser.CUSTOMER)
            if user.check_password(password):
                refresh = RefreshToken.for_user(user)
                access = str(refresh.access_token)
                return Response({"token" : access}, status=status.HTTP_200_OK)
            else:
                return Response({"message" : "invalid password"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message" : "Customer doesn't exist with the given number"}, status=status.HTTP_404_NOT_FOUND)
        

class EmailLogin(APIView):
    def get(self, request):
        email = request.data["email"]
        password = request.data["password"]
        if LykaUser.objects.role_exists_email(email=email, role=LykaUser.CUSTOMER):
            user = LykaUser.objects.get(email=email, role=LykaUser.CUSTOMER)
            if user.check_password(password):
                refresh = RefreshToken.for_user(user)
                access = str(refresh.access_token)
                return Response({"token" : access}, status=status.HTTP_200_OK)
            else:
                return Response({"message" : "invalid password"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message" : "Customer doesn't exist with the given email"}, status=status.HTTP_404_NOT_FOUND)

class PhoneOtpLogin(APIView):
    def get(self, request, phone):
        if LykaUser.objects.role_exists_phone(phone=phone, role=LykaUser.CUSTOMER):
            print(phone)
            user = LykaUser.objects.get(phone=phone, role=LykaUser.CUSTOMER)
            new_otp = otp_generator()
            user.otp = new_otp
            user.save()
            print(new_otp)
            if user:
                return Response({"message" : "success"}, status=status.HTTP_200_OK)
            else:
                return Response({"message" : "failed"}, status=status.HTTP_400_BAD_REQUEST)
            # url = f"https://2factor.in/API/V1/{settings.OTP_AUTH_TOKEN}/SMS/+91{phone}/{new_otp}/OTP1"
            # response = requests.request("GET", url)
            # if response.status_code == 200:
            #     return Response({"message" : "success"}, status=status.HTTP_200_OK)
            # else:
            #     print(response)
            #     return Response({"message" : "failed"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message" : "Customer doesn't exist with the given number"}, status=status.HTTP_404_NOT_FOUND)
        
    def post(self, request):
        phone = request.data["phone"]
        user_typed_code = request.data["user_typed_code"]
        user = LykaUser.objects.get(phone=phone, role=LykaUser.CUSTOMER)
        if user is not None:
                if user.otp == user_typed_code:
                    user.otp = None
                    user.save()
                    refresh = RefreshToken.for_user(user)
                    access = str(refresh.access_token)
                    return Response({"token" : access}, status=status.HTTP_200_OK)
                else:
                    return Response({"message" : "invalid otp"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message" : "user doesn't exist with this number"}, status=status.HTTP_404_NOT_FOUND)


class CustomerCreateView(generics.ListCreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerCreateSerializer

class CustomerUserUpdateView(APIView):
    serializer_class = CustomerUserUpdateSerializer

    def put(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IsCustomerLoggedInOrNot(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        if user.role == LykaUser.CUSTOMER:
            return Response({"name" : user.first_name}, status=status.HTTP_200_OK)
        else:
            return Response({"message" : "User not logged in"}, status=status.HTTP_404_NOT_FOUND)





