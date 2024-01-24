from datetime import datetime, timedelta
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
from .models import *
from .serializers import *

class ProductVerificationView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def patch(self, request, product_id, verification_status):
        try:
            user = request.user
            if not user.role == LykaUser.ADMIN:
                return Response({"message" : "Authentication Failed"}, status=status.HTTP_401_UNAUTHORIZED)
            
            product = Product.objects.get(productId = product_id)
            
            if verification_status == "ACCEPTED":
                product.verified = True
                product.save()
                return Response({"message" : "product has been successfully added to the catalog"}, status=status.HTTP_200_OK)
            elif verification_status == "REJECTED":
                product.delete()
                return Response({"message" : "Product has been deleted"}, status=status.HTTP_200_OK)
            
        except Product.DoesNotExist:
            return Response({"message" : "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class CommissionRetrieveView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        try:
            if request.user.role == LykaUser.ADMIN:
                commissions = Commission.objects.filter(is_successful=True)
                commission_serializer = CommissionSerializer(commissions, many=True)
                return Response(commission_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"message" : "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        except Commission.DoesNotExist:
            return Response({"message" : "Not Found"}, status=status.HTTP_404_NOT_FOUND)
        # except Exception as e:
        #     return Response({"message" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CommissionDaysView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            if request.user.role == LykaUser.ADMIN:
                days = request.data['days']
                transactions_dict = {}
                for day in days:
                    total_amount = 0
                    commissions = Commission.objects.filter(date=day, is_successful=True)
                    if commissions:
                        total_amount = commissions.aggregate(total_amount=Sum('amount'))["total_amount"]
                        transactions_dict[day] = total_amount
                    else:
                        transactions_dict[day] = total_amount
                return Response(transactions_dict, status=status.HTTP_200_OK)
            else:
                return Response({"message" : "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        except Commission.DoesNotExist:
            return Response({"message" : "Not Found"}, status=status.HTTP_404_NOT_FOUND)
        # except Exception as e:
        #     return Response({"message" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class CommissionWeeksView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            if request.user.role == LykaUser.ADMIN:
                weeks = request.data['weeks']
                transactions_dict = {}
                for week in weeks:
                    total_amount = 0
                    startDate, endDate = week.split(" - ")
                    commissions = Commission.objects.filter(date__range=[startDate, endDate], is_successful=True)
                    if commissions:
                        total_amount = commissions.aggregate(total_amount=Sum('amount'))["total_amount"]
                        transactions_dict[week] = total_amount
                    else:
                        transactions_dict[week] = total_amount
                return Response(transactions_dict, status=status.HTTP_200_OK)
            else:
                return Response({"message" : "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        except Commission.DoesNotExist:
            return Response({"message" : "Not Found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message' : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class CommissionMonthsView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_transactions_for_year_and_month(self, year, month):
        start_date = datetime(year, month, 1)
        total_amount = 0
        end_date = None
        if (start_date.month >= 12):
            end_date = start_date.replace(year=start_date.year + 1 ,month=start_date.month - 11, day=1)
        else:
            end_date = start_date.replace(month=start_date.month + 1, day=1) - timedelta(days=1)
        commissions = Commission.objects.filter(date__gte=datetime.date(start_date), date__lte=datetime.date(end_date), is_successful=True)
        if commissions:
            total_amount = commissions.aggregate(total_amount=Sum('amount'))["total_amount"]
        return total_amount

    def post(self, request):
        try:
            if request.user.role == LykaUser.ADMIN:
                years_and_months = request.data["months"]
                transactions_dict = {}
                for data in years_and_months:
                    year, month = data['year'], data['month']
                    transactions_data = self.get_transactions_for_year_and_month(year=year, month=month)
                    key = f"{year}-{month}"
                    transactions_dict[key] = transactions_data
                return Response(transactions_dict, status=status.HTTP_200_OK)
            else:
                return Response({"message" : "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        except LykaUser.DoesNotExist:
            return Response({"message" : "Not Found"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class CommissionYearsView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            if request.user.role == LykaUser.ADMIN:
                years = request.data["years"]
                transactions_dict = {}
                for year in years:
                    total_amount = 0
                    start_year = datetime(year, 1, 1)
                    start_day_of_next_year = datetime(year + 1, 1, 1)
                    end_year = start_day_of_next_year - timedelta(days=1)
                    transactions = Commission.objects.filter(date__range=[start_year, end_year],is_successful=True)
                    if transactions:
                        total_amount = transactions.aggregate(total_amount=Sum('amount'))["total_amount"]
                        transactions_dict[year] = total_amount
                    else:
                        transactions_dict[year] = total_amount
                return Response(transactions_dict, status=status.HTTP_200_OK)
            else:
                return Response({"message" : "Not Found"}, status=status.HTTP_404_NOT_FOUND)
        except Commission.DoesNotExist:
            return Response({"message" : "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CommissionReportRetrieveView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        try:
            if request.user.role == LykaUser.ADMIN:
                commission_report = Total_Commission.calculate_total()
                commission_report_serializer = TotalCommissionSerializer(commission_report, many=False)
                return Response(commission_report_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"message" : "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        except LykaUser.DoesNotExist:
            return Response({"message" : "Not Found"}, status=status.HTTP_404_NOT_FOUND)
        # except Exception as e:
        #     return Response({"message" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


class CommissionReportTimelineView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            if request.user.role == LykaUser.ADMIN:
                start_date = request.data["start_date"]
                end_date = request.data["end_date"]
                commission_report = Total_Commission.calculate_total(start_date=start_date, end_date=end_date)
                commission_report_serializer = TotalCommissionSerializer(commission_report, many=False)
                return Response(commission_report_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"message" : "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        except LykaUser.DoesNotExist:
            return Response({"message" : "Not Found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminLoginView(APIView):
    def post(self, request):
        try:
            email = request.data["email"]
            password = request.data["password"]

            if LykaUser.objects.role_exists_email(email=email, role=LykaUser.ADMIN):
                user = LykaUser.objects.get(email=email, role = LykaUser.ADMIN)
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


