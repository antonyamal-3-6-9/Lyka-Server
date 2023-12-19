from django.shortcuts import render
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from lyka_products.models import Product
from lyka_user.models import LykaUser, BlacklistedToken
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken


class ProductVerificationView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def patch(self, request, product_id, verification_status):
        try:
            user = request.user
            if not user.role == LykaUser.ADMIN:
                return Response({"message" : "Authentication Failed"}, status=status.HTTP_401_UNAUTHORIZED)
            
            product = Product.objects.get(productId = product_id)
            
            if verification_status == True:
                product.verified = True
                product.save()
                return Response({"message" : "product has been successfully added to the list"}, status=status.HTTP_200_OK)
            else:
                product.delete()
                return Response({"message" : "Product has been deleted"}, status=status.HTTP_200_OK)
            
        except Product.DoesNotExist:
            return Response({"message" : "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AdminLoginView(APIView):
    def post(self, request):
        try:
            phone = request.data["phone"]
            password = request.data["password"]

            if LykaUser.objects.role_exists_phone(phone=phone, role=LykaUser.ADMIN):
                user = LykaUser.objects.get(phone=phone, role = LykaUser.ADMIN)
                if user.check_password(password):
                    refresh = RefreshToken.for_user(user)
                    access_token = str(refresh.access_token)
                    return Response({"token" : access_token}, status=status.HTTP_200_OK)
                else:
                    return Response({"message" : "Invalid Password"}, status=status.HTTP_400_BAD_REQUEST)
            else: 
                return Response({"message" : "Admin not found"}, status=status.HTTP_404_NOT_FOUND)
        
        except LykaUser.DoesNotExist:
            return Response({"message" : "Admin not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AdminLogoutView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            auth_header = request.META.get("HTTP_AUTHORIZATION")
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                BlacklistedToken.objects.create(token=token)
                return Response({"message" : "Logged out successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"message" : "Error Logging out"}, status=status.HTTP_400_BAD_REQUEST)
        except BlacklistedToken.DoesNotExist:
            return Response({"message" : "Token not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_400_BAD_REQUEST)


