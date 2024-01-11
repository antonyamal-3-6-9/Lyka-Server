from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import NotificationSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from .models import Notification, LykaUser

# Create your views here.

class NotificationView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            notifications = Notification.objects.filter(owner = request.user)
            serializer = NotificationSerializer(notifications, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response({"message" : "No notifications found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message" : "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class CheckActiveView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            return Response({"user" : {"name" : user.first_name, "id" : user.id, "role" : user.role}}, status=status.HTTP_200_OK)
        except LykaUser.DoesNotExist:
            return Response({"message" : "Authentication Failed"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"message" : "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

