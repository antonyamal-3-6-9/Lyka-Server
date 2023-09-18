from rest_framework.views import APIView
from lyka_order.models import *
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import *


class CustomerAddressCreateView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            customer = Customer.objects.get(user=request.user)
            address_serializer = CustomerAddressSerializer(data=request.data["newAddress"])
            address_serializer.is_valid(raise_exception=True)
            address = address_serializer.save()
            address.owner = customer
            address.save()
            address_to_return = CustomerAddressRetriveSerializer(address, many=False)
            return Response(address_to_return.data, status=status.HTTP_200_OK)
        except Customer.DoesNotExist:
            return Response({"message" : "Authentication failed"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CustomerAddressRetriveView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            customer = Customer.objects.get(user=request.user)
            address = CustomerAddress.objects.filter(owner=customer)
            address_serializer = CustomerAddressRetriveSerializer(address, many=True)
            return Response(address_serializer.data, status=status.HTTP_200_OK)
        except Customer.DoesNotExist:
            return Response({"message" : "Authentication failed"}, status=status.HTTP_401_UNAUTHORIZED)
        except CustomerAddress.DoesNotExist:
            return Response({"message" : "No saved addressess"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomerAddressEditView(generics.UpdateAPIView):
    serializer_class = CustomerAddressSerializer
    queryset = CustomerAddress.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


class StoreAddressEditView(generics.UpdateAPIView):
    serializer_class = SellerStoreAddressSerializer
    queryset = SellerStoreAddress.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


class StoreAddressRetriveView(APIView):
    def get(self, request, address_id):
        user = request.user
        if user is not None:
            try:
                address = SellerStoreAddress.objects.get(id=address_id)
                address_serilizer = SellerStoreAddressRetriveSerializer(address, many=False)
                return Response(address_serilizer.data, status=status.HTTP_200_OK)
            except SellerStoreAddress.DoesNotExist:
                return Response({"message" : "Address doesnot exist"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message" : "Unauthorised"}, status=status.HTTP_401_UNAUTHORIZED)
        
