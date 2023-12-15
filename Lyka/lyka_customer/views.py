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
from lyka_user.models import BlacklistedToken
from rest_framework.permissions import IsAuthenticated
import random
from sendgrid.helpers.mail import Mail

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
    def post(self, request):
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
        
class CustomerOtpView(APIView): 
    def get(self, request, phone):
        if not LykaUser.objects.role_exists_phone(phone=phone, role=LykaUser.CUSTOMER):
            new_otp = otp_generator()
            otp, created = CustomerOtp.objects.get_or_create(verification_credential=phone)
            otp.code = new_otp
            otp.save()
            print(new_otp)
            if otp:
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
        otp = CustomerOtp.objects.get(verification_credential=phone)
        if otp.code == user_typed_code:
            return Response({"message" : 'Success'}, status=status.HTTP_200_OK)
        else:
            return Response({"message" : "invalid otp"}, status=status.HTTP_400_BAD_REQUEST)

        

class CustomerCreateView(generics.ListCreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerCreateSerializer



class EmailOtpVerificationView(APIView):
    auth_token = "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"

    def otp_generator(self):
        otp = random.randint(100000, 999999)
        return str(otp)

    def get(self, request, to_email):
        try:
            verification_code = None
            if CustomerOtp.objects.filter(verification_credential=to_email).exists():
                verification_code = CustomerOtp.objects.get(
                    verification_credential=to_email)
                verification_code.code = self.otp_generator()
                verification_code.save()
            else:
                verification_code = CustomerOtp.objects.create(
                    verification_credential=to_email, code=self.otp_generator())
            message = Mail(
                    from_email='sclera.prog@gmail.com',
                    to_emails=to_email,
                    subject='Lyka Verification',
                    html_content=f'<strong>Your Verification code is <h3>{verification_code.code}</h3></strong>'
                )
            print(message)
            sg = SendGridAPIClient(self.auth_token)
            response = sg.send(message)
            print(response.status_code)
            if response.status_code == 202:
                return Response({"message": "OTP Send successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "OTP creation failed"}, status=status.HTTP_400_BAD_REQUEST)
        except Customer.DoesNotExist:
            return Response({"message": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        try:
            user_typed_code = request.data["user_typed_code"]
            email = request.data["email"]

            verification_code = CustomerOtp.objects.get(
                verification_credential=email)

            if verification_code.code == user_typed_code:
                verification_code.delete()
                return Response({"message" : "verified"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Invalid code"}, status=status.HTTP_400_BAD_REQUEST)
        except Customer.DoesNotExist:
            return Response({"message" : "Unauthorised"}, status=status.HTTP_401_UNAUTHORIZED)


class IsCustomerLoggedInOrNot(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        if user.role == LykaUser.CUSTOMER:
            return Response({"name" : user.first_name}, status=status.HTTP_200_OK)
        else:
            return Response({"message" : "User not logged in"}, status=status.HTTP_404_NOT_FOUND)


class CustomerLogOutView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header and auth_header.startswith('Bearer '):
            jwt_token = auth_header.split(' ')[1]
            BlacklistedToken.objects.create(token=jwt_token)
            return Response({"message" : "Successfully logged out"}, status=status.HTTP_200_OK)
        else:
            return Response({"message" : "Authentication failed"}, status=status.HTTP_401_UNAUTHORIZED)


class  CustomerUserUpdateView(generics.UpdateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerUpdateSerializer
    queryset = Customer.objects.all()


class CustomerProfileRetriveView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        try:
            customer = Customer.objects.get(user=request.user)
            user_serializer = CustomerRetriveSerializer(customer, many=False)
            return Response(user_serializer.data, status=status.HTTP_200_OK)
        except LykaUser.DoesNotExist:
            return Response({"user doesn't exist with the given phone number"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  


class IsPasswordExistsView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        try:
            user = request.user
            if user.role == LykaUser.CUSTOMER:
                if user.has_usable_password():
                    return Response({"message" : "Success"}, status=status.HTTP_200_OK)
                else:
                    return Response({"message" : "Failed"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message" : "Invalid User"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def patch(self, request):
        try:
            user = request.user
            new_password = request.data["new_password"]
            if user.role == LykaUser.CUSTOMER:
                if user.has_usable_password():
                    password = request.data["password"]
                    if user.check_password(password):
                        user.set_password(new_password)
                        user.save()
                        return Response({"message" : "success"}, status=status.HTTP_200_OK)
                    else:
                        return Response({"message" : "Invalid Password"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    user.set_password(new_password)
                    user.save()
                    return Response({"message" : "success"}, status=status.HTTP_200_OK)
            else:
                return Response({"message" : "Invalid user"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        














        