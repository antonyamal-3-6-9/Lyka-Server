from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from lyka_user.models import LykaUser
from rest_framework.views import APIView
from lyka_products.models import Product


class RootAddView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    queryset = Root.objects.all()
    serializer_class = RootSerializer

    def post(self, request):
        user = request.user
        print("hyy")
        if not user.role == LykaUser.ADMIN:
            return Response({"message" : "Authentication Failed"}, status=status.HTTP_401_UNAUTHORIZED)
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

class RootUpdateView(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [JWTAuthentication]
    def patch(self, request):
        try:
            name = request.data["name"]
            root_id = request.data["root_id"]
            if len(name) < 5:
                return Response({"message" : "Name must contain at least five characters"}, status=status.HTTP_400_BAD_REQUEST)
            root = Root.objects.get(root_id=root_id)
            root.name = name
            root.save()
            return Response({"message": "Name updated successfully"}, status=status.HTTP_200_OK)
        except Root.DoesNotExist:
            return Response({"message" : "Not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message" : "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class MainUpdateView(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [JWTAuthentication]
    def patch(self, request):
        try:
            name = request.data["name"]
            main_id = request.data["main_id"]
            root_id = request.data["root_id"]
            if len(name) < 5:
                return Response({"message" : "Name must contain at least five characters"}, status=status.HTTP_400_BAD_REQUEST)
            main = Main.objects.get(main_id=main_id)
            if len(root_id) > 5:
                if not Product.objects.filter(main_category=main).exists():
                    main.root = Root.objects.get(root_id=root_id)
                    main.save()
                    return Response({"message": "Updated successfully"}, status=status.HTTP_200_OK)
                else:
                    return Response({"message" : "Cannot change the root category"}, status=status.HTTP_400_BAD_REQUEST)   
            main.name = name
            main.save()
            return Response({"message" : "Name Updated successfully"}, status=status.HTTP_200_OK)
        except Root.DoesNotExist:
            return Response({"message" : "Not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message" : "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class SubUpdateView(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [JWTAuthentication]
    def patch(self, request):
        try:
            name = request.data["name"]
            sub_id = request.data["sub_id"]
            main_id = request.data["main_id"]
            if len(name) < 5:
                return Response({"message" : "Name must contain at least five characters"}, status=status.HTTP_400_BAD_REQUEST)
            sub = Sub.objects.get(sub_id=sub_id)
            if len(main_id) > 5:
                if not Product.objects.filter(sub_category=sub).exists():
                    sub.main = Main.objects.get(main_id=main_id)
                    sub.save()
                    return Response({"message": "Updated successfully"}, status=status.HTTP_200_OK)
                else:
                    return Response({"message" : "Cannot change the root category"}, status=status.HTTP_400_BAD_REQUEST)  
            sub.name = name 
            sub.save()
            return Response({"message" : "Name Updated successfully"}, status=status.HTTP_200_OK)
        except Root.DoesNotExist:
            return Response({"message" : "Not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message" : "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            

class RootDelete(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [JWTAuthentication]
    def delete(self, request, root_id):
        try:
            root = Root.objects.get(root_id=root_id)
            if Main.objects.filter(root=root).exists() or Product.objects.filter(root_category=root).exists*():
                return Response({"message" : "Selected Category has child categories or products and cannot be deleted"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
            root.delete()
            return Response({"message" : "Successfully deleted"}, status=status.HTTP_200_OK)
        except Root.DoesNotExist:
            return Response({"message" : "Not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message" : "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class MainDelete(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [JWTAuthentication]
    def delete(self, request, main_id):
        try:
            main = Main.objects.get(main_id=main_id)
            if Sub.objects.filter(main=main).exists() or Product.objects.filter(main_category=main).exists*():
                return Response({"message" : "Selected Category has child categories or products and can't be deleted"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
            main.delete()
            return Response({"message" : "Successfully deleted"}, status=status.HTTP_200_OK)
        except Root.DoesNotExist:
            return Response({"message" : "Not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message" : "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class SubDelete(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [JWTAuthentication]
    def delete(self, request, sub_id):
        try:
            sub = Sub.objects.get(sub_id=sub_id)
            if Product.objects.filter(sub_category=sub).exists():
                return Response({"message" : "Selected Category has child categories or products and can't be deleted"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
            sub.delete()
            return Response({"message" : "Successfully deleted"}, status=status.HTTP_200_OK)
        except Root.DoesNotExist:
            return Response({"message" : "Not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message" : "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CategoryListView(APIView):
    def get(self, request):
        try:
            root = Root.objects.all()
            main = Main.objects.all()
            sub = Sub.objects.all()

            root_serializer = RootViewSerializer(root, many=True)
            main_serializer = MainViewSerializer(main, many=True)
            sub_serializer = SubViewSerializer(sub, many=True)

            return Response({"root" : root_serializer.data, "main" : main_serializer.data, "sub" : sub_serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message" : "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
