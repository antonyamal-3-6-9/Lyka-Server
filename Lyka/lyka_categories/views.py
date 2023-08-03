from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework import generics

# Create your views here.

class RootAddView(generics.ListCreateAPIView):
    queryset = Root.objects.all()
    serializer_class = RootSerializer

class MainAddView(generics.ListCreateAPIView):
    queryset = Main.objects.all()
    serializer_class = MainSerializer

class SubAddView(generics.ListCreateAPIView):
    queryset = Sub.objects.all()
    serializer_class = SubSerializer

class RootView(generics.ListAPIView):
    queryset = Root.objects.all()
    serializer_class = RootViewSerializer

class MainView(generics.ListAPIView):
    queryset = Main.objects.all()
    serializer_class = MainViewSerializer

class SubView(generics.ListAPIView):
    queryset = Sub.objects.all()
    serializer_class = SubViewSerializer
