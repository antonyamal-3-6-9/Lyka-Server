from .serializers import *
from rest_framework import generics
from .models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from rest_framework_simplejwt.authentication import JWTAuthentication
from lyka_user.models import BlacklistedToken, UserCreationAuth
from rest_framework.permissions import IsAuthenticated
import random
from sendgrid.helpers.mail import Mail
import secrets, string
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from datetime import datetime



def otp_generator():
    otp = random.randint(100000, 999999)
    return str(otp)

class CustomerExistsOrNot(APIView):
    def get(self, request, phone_number):
        if LykaUser.objects.role_exists_phone(phone=phone_number, role=LykaUser.CUSTOMER):
            return Response({"message" : "Customer already exists with the same number"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message" : "Phone number is not used"}, status=status.HTTP_200_OK)  


def generate_token():
    token = secrets.token_hex(6).upper()
    return token


class CustomerRequestView(APIView):
    def get(self, request, email, *args, **kwargs):
        try:
            if LykaUser.objects.role_exists_email(email=email, role=LykaUser.CUSTOMER):
                return Response({"message" : "User Already Exists"}, status=status.HTTP_208_ALREADY_REPORTED)
            customer_auth = None
            if UserCreationAuth.objects.filter(email=email, role=UserCreationAuth.CUSTOMER).exists():
                customer_auth = UserCreationAuth.objects.get(email = email, role = UserCreationAuth.CUSTOMER)
            else:
                customer_auth = UserCreationAuth.objects.create(email = email, role = UserCreationAuth.CUSTOMER)
            customer_auth.token = generate_token()
            customer_auth.save()
            message = Mail(
                    from_email='sclera.prog@gmail.com',
                    to_emails=email,
                    subject='Lyka User Verification',
                    html_content = f"<div><p>Please click on the below link to verify your email and set a password</p><a href=http://localhost:3000/customer/auth/verify/{customer_auth.email}/{customer_auth.token}>http://localhost:3000/customer/auth/verify/{customer_auth.email}/{customer_auth.token}</a></div>"

                )
            sg = SendGridAPIClient(settings.SEND_GRID_KEY)
            response = sg.send(message)
            if response.status_code == 202:
                return Response({"message" : f"Verification link has been send to {customer_auth.email}"}, status=status.HTTP_200_OK)
            else:
                return Response({"message" : "Error sending link"}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError:
            return Response({"message" : "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def post(self, request):
        try:
            email = request.data["email"]
            token = request.data["token"]
            if UserCreationAuth.objects.filter(email=email, role=LykaUser.CUSTOMER).exists():
                usercreation_auth = UserCreationAuth.objects.get(email=email, role=LykaUser.CUSTOMER)
                print(token, usercreation_auth.token)
                if usercreation_auth.token == token:
                    return Response({"message" : "Email Successfully Verified"}, status=status.HTTP_200_OK)
                else:
                    return Response({"message" : "Verification Link Expired"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({"message" : "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            

class CustomerCreateView(generics.CreateAPIView):

    def post(self, request):
        try:
            email = request.data["email"]
            password = request.data["password"]
            token = request.data["token"]

            if UserCreationAuth.objects.filter(email=email, token=token, role=LykaUser.CUSTOMER).exists():
                if not LykaUser.objects.role_exists_email(email=email, role=LykaUser.CUSTOMER):
                    lyka_user_instance, created = LykaUser.objects.get_or_create(email=email, role=LykaUser.CUSTOMER)
                    customer = Customer.objects.create(user=lyka_user_instance)
                    customer.user.set_password(password)
                    usercreation_auth = UserCreationAuth.objects.get(email=email, token=token, role=UserCreationAuth.CUSTOMER)
                    usercreation_auth.delete()
                    refresh = RefreshToken.for_user(lyka_user_instance)
                    access_token = str(refresh.access_token)
                    if access_token:
                        return Response({"token" : access_token}, status=status.HTTP_200_OK)
                    else:
                        return Response({"message" : "token generation failed"}, status.HTTP_408_REQUEST_TIMEOUT)
                else:
                    return Response({"message" : " customer does not exist"}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"message" : "Verification link expired"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        # except Exception as e:
        #     return Response({"message" : "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except UserCreationAuth.DoesNotExist:
            return Response({"message" : "Link expired"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        except LykaUser.DoesNotExist:
            return Response({"message" : "Invalid Customer"}, status=status.HTTP_404_NOT_FOUND)
            

class PasswordLoginView(APIView):
    def get(self, request):
        email = request.data["email"]
        password = request.data["password"]
        if LykaUser.objects.role_exists_email(email=email, role=LykaUser.CUSTOMER):
            user = LykaUser.objects.get(email=email, role=LykaUser.CUSTOMER)
            if user.check_password(password):
                refresh = RefreshToken.for_user(user)
                access = str(refresh.access_token)
                return Response({"user" : {"name" : user.first_name, "id" : user.id},"token" : access}, status=status.HTTP_200_OK)
            else:
                return Response({"message" : "invalid password"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message" : "Customer doesn't exist with the given email"}, status=status.HTTP_404_NOT_FOUND)
        
class OtpLoginView(APIView):
    def otp_generator(self):
        otp = random.randint(100000, 999999)
        return str(otp)

    def get(self, request, email):
        try:
            verification_code = None
            if LykaUser.objects.role_exists_email(email=email, role=LykaUser.CUSTOMER):
                if CustomerOtp.objects.filter(verification_credential=email).exists():
                    verification_code = CustomerOtp.objects.get(
                        verification_credential=email)
                    verification_code.code = self.otp_generator()
                    verification_code.save()
                else:
                    verification_code = CustomerOtp.objects.create(
                        verification_credential=email, code=self.otp_generator())
                message = Mail(
                        from_email='sclera.prog@gmail.com',
                        to_emails=email,
                        subject='Lyka OTP Verification',
                        html_content=f'<strong>Your Verification code is <h3>{verification_code.code}</h3></strong>'
                    )
                print(verification_code.code)
                sg = SendGridAPIClient(settings.SEND_GRID_KEY)
                response = sg.send(message)
                print(response.status_code)
                if response.status_code == 202:
                    return Response({"message": "OTP Send successfully"}, status=status.HTTP_200_OK)
                else:
                    return Response({"message": "OTP creation failed"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message" : "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        except Customer.DoesNotExist:
            return Response({"message": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        try:
            user_typed_code = request.data["otp"]
            email = request.data["email"]

            verification_code = CustomerOtp.objects.get(
                verification_credential=email)
            
            if verification_code.code == user_typed_code:
                user = LykaUser.objects.get(email=email, role=LykaUser.CUSTOMER)
                verification_code.delete()
                refresh = RefreshToken.for_user(user)
                access = str(refresh.access_token)
                return Response({"user" : {"name" : user.first_name, "id" : user.id},"token" : access}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
        except Customer.DoesNotExist:
            return Response({"message" : "Unauthorised"}, status=status.HTTP_401_UNAUTHORIZED)
        except CustomerOtp.DoesNotExist:
            return Response({"message" : "Invalid OTP"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message" : "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class EmailOtpVerificationView(APIView):
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
                    subject='Lyka OTP Verification',
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
        except CustomerOtp.DoesNotExist:
            return Response({"otp not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message" : "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class IsCustomerLoggedInOrNot(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        print(user.role)
        if user.role == LykaUser.CUSTOMER:
            return Response({"user" : {"name" : user.first_name, "id" : user.id}}, status=status.HTTP_200_OK)
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
        # except Exception as e:
        #     return Response({"message" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  


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
        














        