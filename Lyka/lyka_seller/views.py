import requests
from rest_framework.views import APIView
from .models import *
from .serializers import *
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from lyka_user.models import BlacklistedToken
from datetime import date
import random
import re


def otp_generator():
    otp = random.randint(100000, 999999)
    return str(otp)

class SellerExistsOrNot(APIView):
    def get(self, request):
        phone = request.query_params.get("phone")
        email = request.query_params.get("email")
        if LykaUser.objects.role_exists_email(email=email, role=LykaUser.SELLER):
            return Response({"message": "Seller already exists with this email"}, status=status.HTTP_226_IM_USED)
        elif LykaUser.objects.role_exists_phone(phone=phone, role=LykaUser.SELLER):
            return Response({"message": "Seller already exists with this phone"}, status=status.HTTP_226_IM_USED)
        else:
            return Response({"message": "Seller doesn't exist with the given credentials"}, status=status.HTTP_200_OK)


class PasswordLoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        
        try:
            user = LykaUser.objects.get(email=email, role=LykaUser.SELLER)
        except LykaUser.DoesNotExist:
            return Response({"message": "Seller doesn't exist with the given email"}, status=status.HTTP_404_NOT_FOUND)

        if user.check_password(password):
            refresh = RefreshToken.for_user(user)
            access = str(refresh.access_token)
            return Response({"token": access}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Incorrect Password"}, status=status.HTTP_400_BAD_REQUEST)
        

class OtpLoginView(APIView):
    def otp_generator(self):
        otp = random.randint(100000, 999999)
        return str(otp)

    def get(self, request, to_email):
        try:
            verification_code = None
            if LykaUser.objects.role_exists_email(email=to_email, role=LykaUser.SELLER):
                if SellerOtp.objects.filter(verification_credential=to_email).exists():
                    verification_code = SellerOtp.objects.get(
                        verification_credential=to_email)
                    verification_code.otp = self.otp_generator()
                    verification_code.save()
                else:
                    verification_code = SellerOtp.objects.create(
                        verification_credential=to_email, otp=self.otp_generator())
                message = Mail(
                        from_email='sclera.prog@gmail.com',
                        to_emails=to_email,
                        subject='Lyka Verification',
                        html_content=f'<strong>Your Verification code is <h3>{verification_code.otp}</h3></strong>'
                    )
                sg = SendGridAPIClient(settings.SEND_GRID_KEY)
                response = sg.send(message)
                print(response.status_code)
                print(verification_code.otp)
                if response.status_code == 202:
                    return Response({"message": "OTP Send successfully"}, status=status.HTTP_200_OK)
                else:
                    return Response({"message": "OTP creation failed"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message" : "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except LykaUser.DoesNotExist:
            return Response({"message": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        try:
            user_typed_code = request.data["otp"]
            email = request.data["email"]
            verification_code = SellerOtp.objects.get(
                verification_credential=email)

            if verification_code.otp == user_typed_code:
                verification_code.delete()
                user = LykaUser.objects.get(email=email, role=LykaUser.SELLER)
                refresh = RefreshToken.for_user(user)
                access = str(refresh.access_token)
                return Response({"token" : access}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Invalid code"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message" : "Login failed"}, status=status.HTTP_401_UNAUTHORIZED)


class EmailOtpVerificationView(APIView):
    def otp_generator(self):
        otp = random.randint(100000, 999999)
        return str(otp)

    def get(self, request, to_email):
        try:
            verification_code = None
            user = request.user
            if SellerOtp.objects.filter(verification_credential=to_email).exists():
                verification_code = SellerOtp.objects.get(
                    verification_credential=to_email)
                verification_code.otp = self.otp_generator()
                verification_code.save()
            else:
                verification_code = SellerOtp.objects.create(
                    verification_credential=to_email, otp=self.otp_generator())
            message = Mail(
                    from_email='sclera.prog@gmail.com',
                    to_emails=to_email,
                    subject='Lyka Verification',
                    html_content=f'<strong>Your Verification code is <h3>{verification_code.otp}</h3></strong>'
                )
            sg = SendGridAPIClient(settings.SEND_GRID_KEY)
            response = sg.send(message)
            print(response.status_code)
            if response.status_code == 202:
                return Response({"message": "OTP Send successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "OTP creation failed"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        try:
            user_typed_code = request.data["otp"]
            email = request.data['email']
            verification_code = SellerOtp.objects.get(
                verification_credential=email)

            if verification_code.otp == user_typed_code:
                verification_code.delete()
                return Response({"message" : "verified"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Invalid code"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_401_UNAUTHORIZED)


class SellerAddressVerificationView(generics.CreateAPIView):
    queryset = AddressProof.objects.all()
    serializer_class = AddressProofSerializer

    def validate_document(self,  document_number, document_type):
        aadhar_pattern = r"^\d{12}$"
        licence_pattern = r"^[A-Z0-9]{16}$"
        voter_id_pattern = r"^[A-Z0-9]{10}$"
        if document_type == "aadhaar":
            if not bool(re.match(aadhar_pattern, document_number)):
                raise ValueError("Invalid Aadhaar number. It should be a 12-digit numeric value.")
        elif document_type == "driving licence":
            if not bool(re.match(licence_pattern, document_number)):
                raise ValueError("Invalid Driving License number. It should be a 16-digit alphanumeric value.")
        elif document_type == "voter id":
            if not bool(re.match(voter_id_pattern, document_number)):
                raise ValueError("Invalid Voter ID number. It should be a 10-character alphanumeric value.")
        else:
            raise ValueError("Invalid document type.")
        
    def check_age_above_eighteen(self, date_of_birth):
        try:
            year, month, day = map(int, date_of_birth.split('-'))
            dob = date(year, month, day)
        except ValueError:
            raise ValueError("Invalid date format. Please provide the date in dd/mm/yyyy format.")

        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

        if age >= 18:
            return True
        else:
            return False

    def put(self, request, *args, **kwargs):
        try:
            address_num = request.data["address_proof_number"]
            address_type = request.data["address_proof_type"]
            address_dob = request.data["address_proff_dob"]
            seller = Seller.objects.get(user=request.user)

            if not  self.check_age_above_eighteen(address_dob):
                return Response({"message" : "You have to be above 18 to sell on Lyka"}, status=status.HTTP_400_BAD_REQUEST)

            self.validate_document(address_num, address_type)

            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            address = serializer.save()
            

            if seller and address:
                seller.address_proof = address
                seller.address_verified = True
                seller.is_verified()
                seller.save()

            if seller.address_verified:
                return Response({"message": "Verified Successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Verification Failed"}, status=status.HTTP_400_BAD_REQUEST)
            
        except Seller.DoesNotExist:
            return Response({"message" : "Seller Doesn't exist"}, status=status.HTTP_401_UNAUTHORIZED)
        except ValueError as e:
            return Response({"message" : str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({"message" : str(e)}, status=status.HTTP_502_BAD_GATEWAY)


class SellerPanVerificationView(generics.CreateAPIView):
    queryset = PanCard.objects.all()
    serializer_class = PanCardSerializer

    def validate_pancard(self, pan_number):
            pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]$'
            if not bool(re.match(pattern, pan_number)):
                raise ValueError("Invalid PAN card number. It should be a 10-character alphanumeric value.")

    def put(self, request, *args, **kwargs):
        try:    
            pan_number = request.data["pan_number"]
            seller = Seller.objects.get(user=request.user)
            self.validate_pancard(pan_number)
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            pan = serializer.save()
            

            if pan and seller:
                seller.pan_card = pan
                seller.pan_verified = True
                seller.is_verified()
                seller.save()

            if seller.pan_verified:
                return Response({"message": "success"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "failed"}, status=status.HTTP_400_BAD_REQUEST)
        except Seller.DoesNotExist:
            return Response({"message" : "Seller Doesn't exist"}, status=status.HTTP_401_UNAUTHORIZED)
        except ValueError as e:
            return Response({"message" : str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({"message" : str(e)}, status=status.HTTP_502_BAD_GATEWAY)


class SellerBankVerificationView(generics.CreateAPIView):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer

    def validate_bank_details(self, account_number, ifsc_code, bank_name, account_holder_name, bank_branch):
        pattern = r"^([A-Z][a-zA-Z]+\s?)+$"
        ifsc_pattern = r"^([A-Z]{4}[0-9]{7})$"

        if len(account_number) < 10 or len(account_number) > 15 or not account_number.isdigit():
            raise ValueError("Invalid account number. It should be a 10-digit numeric value.")

        if not bool(re.match(ifsc_pattern, ifsc_code)):
            raise ValueError("Invalid IFSC code. It should be an 11-character alphanumeric value.")
        
        if not bool(re.match(pattern, bank_name)):
            raise ValueError("Invalid Bank Name, The name must start with an uppercase Charector")
        
        if not bool(re.match(pattern, account_holder_name)):
            raise ValueError("Invalid Account Holder Name, The name must start with an uppercase charector")
        
        if not bool(re.match(pattern, bank_branch)):
            raise ValueError("Invalid Bank Branch, The name must start with an uppercase charector")
        

    def put(self, request, *args, **kwargs):
        try:
            account_number = request.data["account_number"]
            bank_ifsc = request.data["bank_ifsc"]
            account_holder_name = request.data["account_holder_name"]
            bank_name = request.data["bank_name"]
            bank_branch = request.data["bank_branch"]
            print(request.data)
            seller = Seller.objects.get(user=request.user)
            self.validate_bank_details(account_number, bank_ifsc, bank_name, account_holder_name, bank_branch)
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            bank = serializer.save()
            

            if bank and seller:
                seller.bank_account = bank
                seller.bank_account_verified = True
                seller.is_verified()
                seller.save()

            if seller.bank_account_verified:
                return Response({"message": "success"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "failed"}, status=status.HTTP_400_BAD_REQUEST)
        except Seller.DoesNotExist:
            return Response({"message" : "Seller doesn't exist"}, status=status.HTTP_401_UNAUTHORIZED)
        except ValueError as e:
            return Response({"message" : str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({"message" : str(e)}, status=status.HTTP_502_BAD_GATEWAY)


class SellerGstVerificationView(generics.CreateAPIView):
    queryset = GstRegistrationNumber.objects.all()
    serializer_class = GstRegistrationNumberSerializer

    def validate_gstin(self, gstin):
        pattern = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"
        if not re.match(pattern, gstin):
            raise ValueError("Invalid GSTIN.")

    def put(self, request, *args, **kwargs):
        try:
            gstin = request.data["gst_number"]
            seller = Seller.objects.get(user=request.user)
            self.validate_gstin(gstin)
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            gst = serializer.save()
            if gst and seller:
                seller.gstin = gst
                seller.gstin_verified = True
                seller.is_verified()
                seller.save()

            if seller.gstin_verified:
                return Response({"message": "success"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "failed"}, status=status.HTTP_400_BAD_REQUEST)
        except Seller.DoesNotExist:
            return Response({"message" : "Seller doesn't exist"}, status=status.HTTP_401_UNAUTHORIZED)
        except ValueError as e:
            return Response({"message" : str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({"message" : str(e)}, status=status.HTTP_502_BAD_GATEWAY)



class SellerLoggedInOrNot(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role == LykaUser.SELLER:
            return Response({"message": "user is logged in"}, status=status.HTTP_200_OK)
        else:
            return Response({"message" : "Not logged in"}, status=status.HTTP_404_NOT_FOUND)


class SellerCreateView(generics.ListCreateAPIView):
    queryset = Seller.objects.all()
    serializer_class = SellerCreationSerializer


class SellerRetriveView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]    
    def get(self, request):
        try:
            user = request.user
            seller = Seller.objects.get(user=user)
            serializer = SellerUserGetSerializer(seller, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"message": "Seller not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AddPickUpStoreView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]    
    def post(self, request):
        try:
            user = request.user
            seller = Seller.objects.get(user=user)

            store_name = request.data.get("store_name")

            address_serializer = SellerStoreAddressSerializer(
                data=request.data)
            address_serializer.is_valid(raise_exception=True)
            address = address_serializer.save()

            store_serializer = PickupStoreSerializer(
                data={"store_name": store_name})
            store_serializer.is_valid(raise_exception=True)
            store = store_serializer.save()

            store.owner = seller
            store.store_address = address
            store.save()

            store_data = PickupStoreViewSerializer(store, many=False)
            return Response(store_data.data, status=status.HTTP_200_OK)
        except Seller.DoesNotExist:
            return Response({"message": "Seller doesn't exist"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PickupStoreRetirveView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]    
    def get(self, request):
        try:
            user = request.user
            seller = Seller.objects.get(user=user)
            stores = PickupStore.objects.filter(owner=seller)
            store_serializer = PickupStoreViewSerializer(stores, many=True)
            return Response(store_serializer.data, status=status.HTTP_200_OK)
        except Seller.DoesNotExist:
            return Response({"messsage": "Seller does not exist"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PickUpStoreDeleteView(generics.DestroyAPIView):
    serializer_class = PickupStoreViewSerializer
    queryset = PickupStore.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


class SellerVerifiedOrNOt(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            user = request.user
            seller = Seller.objects.get(user=user)
            seller_serializer = SellerVerifiedSerializer(seller, many=False)
            return Response(seller_serializer.data, status=status.HTTP_200_OK)
        except Seller.DoesNotExist:
            return Response({"message": "Seller doesn't exist"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class GetSellerView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]    
    def get(self, request):
        try:
            user = request.user
            seller = Seller.objects.get(user=user)
            seller_serializer = SellerGetSerializer(seller, many=False)
            return Response(seller_serializer.data, status=status.HTTP_200_OK)
        except Seller.DoesNotExist:
            return Response({"message": "Seller doesn't exist"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UpdateSellerProfile(generics.UpdateAPIView):
    serializer_class = SellerUpdateSerializer
    queryset = Seller.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


class SellerPasswordChangeView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            existing_password = request.data["existing_password"]
            new_password = request.data["new_password"]

            user = request.user
            if user.check_password(existing_password):
                user.set_password(new_password)
                user.save()
                return Response({"message": "Password has been updated successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "You entered the incorrect password"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        except KeyError as e:
            return Response({"message": f"Missing required field: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SellerLogOutView(APIView):
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
        

class IsStoreExistsOrNot(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            seller = Seller.objects.get(user=request.user)
            if PickupStore.objects.get(owner=seller).exists():
                return Response({"message" : "Pickup store exists"}, status=status.HTTP_200_OK)
            else:
                return Response({"message" : "Pickup store doesn't exist"}, status=status.HTTP_404_NOT_FOUND)
        except Seller.DoesNotExist:
            return Response({"message" : "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        