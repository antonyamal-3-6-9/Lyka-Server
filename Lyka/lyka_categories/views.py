from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from lyka_user.models import LykaUser
# Create your views here.

class RootAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    queryset = Root.objects.all()
    serializer_class = RootSerializer

    def post(self, request):
        user = request.user
        if not user.role == LykaUser.ADMIN:
            return Response({"message" : "Authentication Failed"})
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class MainAddView(generics.ListCreateAPIView):
    queryset = Main.objects.all()
    serializer_class = MainSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        user = request.user
        if not user.role == LykaUser.ADMIN:
            return Response({"message" : "Authentication Failed"})
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class SubAddView(generics.ListCreateAPIView):
    queryset = Sub.objects.all()
    serializer_class = SubSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        user = request.user
        if not user.role == LykaUser.ADMIN:
            return Response({"message" : "Authentication Failed"})
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RootView(generics.ListAPIView):
    queryset = Root.objects.all()
    serializer_class = RootViewSerializer

class MainView(generics.ListAPIView):
    queryset = Main.objects.all()
    serializer_class = MainViewSerializer

class SubView(generics.ListAPIView):
    queryset = Sub.objects.all()
    serializer_class = SubViewSerializer
