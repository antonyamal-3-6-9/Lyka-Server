from django.shortcuts import render
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from lyka_products.models import Product
from lyka_user.models import LykaUser
from rest_framework import status
from rest_framework.response import Response

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





        
