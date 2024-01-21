import base64
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from lyka_products.models import Unit
import requests
from .signals import order_placed
from rest_framework import generics
from lyka_customer.models import Customer
from lyka_seller.models import Seller
from .serializers import *
from .models import *
from lyka_order.models import *
from django.conf import settings
import razorpay
import hmac
import hashlib
import time
import secrets
import stripe
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from lyka_user.models import Notification


def generate_unique_payment_id():
    timestamp = int(time.time() * 1000) 
    random_string = secrets.token_hex(4).upper()
    payment_id = f'{timestamp}{random_string}'
    return payment_id

def send_order_update_notification(user_id, message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'user_{user_id}',
        {
            'type': 'send_order_update',
            'message': message,
        }
    )

def update_order(lyka_order_id, payment_method):
    if OrderGroup.objects.filter(order_list_id=lyka_order_id).exists():   
        orders = Order.objects.filter(order_list__order_list_id=lyka_order_id)
        for order in orders:
            order.payment_method = payment_method
            order.payment_status = True
            order.status = Order.PLACED
            credentials = OrderCredentials.objects.create()
            order.credentials = credentials
            order.credentials.payment_id = generate_unique_payment_id()
            order.credentials.save()
            order.save()
            unit = Unit.objects.get(variant=order.item.product_variant,
                                    color_code=order.item.product_color, product=order.item.product, seller=order.seller)
            old_stock = unit.stock
            new_stock = int(old_stock) - int(order.item.quantity)
            unit.stock = new_stock
            unit.save()
            message_c=f'Your order for {order.item.product.brand} {order.item.product.name} has been successfully placed at {order.time}'
            message_s=f'Your order for {order.item.product.brand} {order.item.product.name} has been successfully placed at {order.time}'
            send_order_update_notification(user_id=order.customer.user.id, message=message_c)
            send_order_update_notification(user_id=order.seller.user.id, message=message_s)
            notification_c = Notification.objects.create(owner=order.customer.user, message=message_c)
            notification_s = Notification.objects.create(owner=order.seller.user, message=message_s)
        return True
    elif Order.objects.filter(order_id=lyka_order_id).exists():
        order = Order.objects.get(order_id=lyka_order_id)
        order.payment_method = payment_method
        order.payment_status = True
        order.status = Order.PLACED
        credentials = OrderCredentials.objects.create()
        order.credentials = credentials
        order.credentials.payment_id = generate_unique_payment_id()
        order.credentials.save()
        order.save()
        unit = Unit.objects.get(variant=order.item.product_variant,
                                color_code=order.item.product_color, product=order.item.product, seller=order.seller)
        old_stock = unit.stock
        new_stock = int(old_stock) - int(order.item.quantity)
        unit.stock = new_stock
        unit.save()
        message_c=f'Your order for {order.item.product.brand} {order.item.product.name} has been successfully placed at {order.time}'
        message_s=f'Your order for {order.item.product.brand} {order.item.product.name} has been successfully placed at {order.time}'
        send_order_update_notification(user_id=order.customer.user.id, message=message_c)
        send_order_update_notification(user_id=order.seller.user.id, message=message_s)
        notification_c = Notification.objects.create(owner=order.customer.user, message=message_c)
        notification_s = Notification.objects.create(owner=order.seller.user, message=message_s)
        return True
    else:
        return False
    

def get_amount_and_check(order_id):
    if OrderGroup.objects.filter(order_list_id=order_id).exists():
        order_list = OrderGroup.objects.get(order_list_id=order_id)
        amount = (int(order_list.total_price) * 10)
        orders = Order.objects.filter(
                order_list__order_list_id=order_id)
        for order in orders:
            unit = Unit.objects.get(
                variant=order.item.product_variant, color_code=order.item.product_color, seller=order.seller, product=order.item.product)
            if unit.stock <= 0:
                return None
        return amount
    elif Order.objects.filter(order_id=order_id).exists():
        order = Order.objects.get(order_id=order_id)
        amount = (int(order.item.product_price) * 10)
        unit = Unit.objects.get(variant=order.item.product_variant,
                    color_code=order.item.product_color, seller=order.seller, product=order.item.product)
        if unit.stock <= 0:
            return None
        else:
            return amount 


class RazorPayOrderPaymentCreationView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def razorpay_order(self, amount, customer_name):

        client = razorpay.Client(
            auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))
        DATA = {
            "amount": amount,
            "currency": "INR",
            "receipt": customer_name,
        }
        return client.order.create(data=DATA)

    def post(self, request):
        try:
            order_id = request.data["order_id"]
            amount = None
            user = request.user
            customer = Customer.objects.get(user=user)
            amount = get_amount_and_check(order_id)
            if amount is None:
                return Response({"message": f'One of your item is out of stock'}, status=status.HTTP_400_BAD_REQUEST) 
            customer_full_name = f'{customer.user.first_name} {customer.user.last_name }'
            order = self.razorpay_order(amount, customer_full_name)
            if order["status"] == "created":
                return Response({"order": order, "test_id": settings.RAZORPAY_API_KEY}, status=status.HTTP_200_OK)
            else:
                return Response({"messsage": "Order failed"}, status=status.HTTP_400_BAD_REQUEST)
        except Customer.DoesNotExist:
            return Response({"message": "Authentication failed"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RazorPayOrderPaymentCaptureView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    payment_id = None
    order_id = None
    razorpay_signature = None
    lyka_order_id = None

    def verify_signature(self):
        credentials = self.order_id + "|" + self.payment_id
        generated_signature = hmac.new(settings.RAZORPAY_API_SECRET.encode(
        ), credentials.encode(), hashlib.sha256).hexdigest()

        if generated_signature == self.razorpay_signature:
            return True
        else:
            return False

    def post(self, request):
        self.payment_id = request.data["payment_id"]
        self.order_id = request.data["order_id"]
        self.razorpay_signature = request.data["razorpay_signature"]
        self.lyka_order_id = request.data["lyka_order_id"]
        if self.verify_signature():
            client = razorpay.Client(
                auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))
            r_order = client.order.fetch(self.order_id)
            try:
                response = client.payment.capture(
                    self.payment_id, r_order["amount"])
                if response.get("status") == "captured":
                    if update_order(lyka_order_id=self.lyka_order_id, payment_method="RAZORPAY"):
                        return Response({"message": "payment successful and order has been placed"}, status=status.HTTP_200_OK)
                    else:
                        refund = client.payment.refund(self.payment_id, {
                                "amount": r_order["amount"],
                                "speed": "normal"
                            })
                        if refund["status"] == "processed":
                            return Response({"message": "Order has been failed, refund has been initiated"}, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            return Response({"message": "Order has been failed, Refund will be initiated within 4-5 bussiness days"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"message": "Payment Capture Failed"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"message" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"message": "Payment Signature Failed"}, status=status.HTTP_400_BAD_REQUEST)


class PaypalPaymentView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def generate_access_token(self):
        auth = base64.b64encode(
            f"{settings.PAYPAL_CLIENT_ID}:{settings.PAYPAL_CLIENT_SECRET}".encode(
                "utf-8")
        ).decode("utf-8")
        response = requests.post(
            f"https://api-m.sandbox.paypal.com/v1/oauth2/token",
            headers={
                "Authorization": f"Basic {auth}",
            },
            data="grant_type=client_credentials",
        )
        data = response.json()
        return data["access_token"]

    def post(self, request):
        order_id = request.data["order_id"]
        order = None
        amount = get_amount_and_check(order_id)
        if amount is None:
            return Response({"message": f'One of your item is out of stock'}, status=status.HTTP_400_BAD_REQUEST) 
        access_token = self.generate_access_token()
        headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
        payload = {
            "intent": "CAPTURE",
            "purchase_units": [{
                "amount": {"currency_code": "USD", "value": int(amount/80)},
                "reference_id": generate_unique_payment_id()
            }]
        }

        try:
            response = requests.post("https://api-m.sandbox.paypal.com/v2/checkout/orders", json=payload, headers=headers)
            data = response.json()
            if data["status"] == "CREATED":
                return Response({"order_id": data["id"]}, status=status.HTTP_200_OK)
            else:
                return Response({"message" : "Failed, Try other payment options"}, status=status.HTTP_400_BAD_REQUEST)
        except requests.exceptions.RequestException as e:
            return Response({"message": "Failed to create order."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, paypal_order_id, lyka_order_id):
        access_token = self.generate_access_token()
        headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',  
        }

        try:
            response = requests.post(f"https://api-m.sandbox.paypal.com/v2/checkout/orders/{paypal_order_id}/capture", headers=headers)
            status = response.data["status"]
            if status == "COMPLETED":
                update_order(lyka_order_id=lyka_order_id, payment_method="PAYPAL")
                return Response({"message" : status}, status=status.HTTP_200_OK)
            else:
                return Response({"message" : "Payment Failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except requests.exceptions.RequestException as e:
            return Response({"message": "Failed to capture payment."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StripePaymentView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def post(self, request):
        try:
            order_id = request.data["order_id"]
            amount = get_amount_and_check(order_id)
            if amount is None:
                return Response({"message": f'One of your item is out of stock'}, status=status.HTTP_400_BAD_REQUEST)
                
            stripe.api_key = settings.STRIPE_API_KEY

            intent = stripe.PaymentIntent.create(
                    amount=amount,
                    currency='inr',
                    automatic_payment_methods={
                        "enabled" : True,
                    }
                )
            return Response({"secret" : intent["client_secret"]}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def patch(self, request):
        try:
            order_id = request.data["order_id"]
            payment_status = request.data["payment_status"]
            if payment_status == "succeeded":
                update_order(lyka_order_id=order_id, payment_method="STRIPE")
                return Response({"message" : "Payment has been successful"}, status=status.HTTP_200_OK)
            else:
                return Response({"message" : "Payment error"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CouponRetriveView(generics.ListAPIView):
    serializer_class = CouponSerializer
    queryset = CouponType.objects.all()


class SalesRetriveView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        try:
            seller = Seller.objects.get(user=request.user)
            transactions = OrderTransaction.objects.filter(payee=seller, is_successful=True)
            transaction_serializer = TransactionRetriveSerializer(transactions, many=True)
            return Response(transaction_serializer.data, status=status.HTTP_200_OK)
        except Seller.DoesNotExist:
            return Response({"message" : "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SalesDaysRetriveView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            days = request.data['days']
            seller = Seller.objects.get(user=request.user)
            transactions_dict = {}
            for day in days:
                total_amount = 0
                transactions = OrderTransaction.objects.filter(payee = seller, date=day, is_successful=True)
                if transactions:
                    total_amount = transactions.aggregate(total_amount=Sum('amount'))["total_amount"]
                    transactions_dict[day] = total_amount
                else:
                    transactions_dict[day] = total_amount
            return Response(transactions_dict, status=status.HTTP_200_OK)
        except Seller.DoesNotExist:
            return Response({"message" : "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class SalesWeekView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            weeks = request.data['weeks']
            transactions_dict = {}
            seller = Seller.objects.get(user=request.user)
            for week in weeks:
                total_amount = 0
                startDate, endDate = week.split(" - ")
                transactions = OrderTransaction.objects.filter(date__range=[startDate, endDate], payee=seller, is_successful=True)
                if transactions:
                    total_amount = transactions.aggregate(total_amount=Sum('amount'))["total_amount"]
                    transactions_dict[week] = total_amount
                else:
                    transactions_dict[week] = total_amount
            return Response(transactions_dict, status=status.HTTP_200_OK)
        except Seller.DoesNotExist:
            return Response({"message" : "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'message' : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class SalesMonthView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_transactions_for_year_and_month(self, year, month, seller):
        start_date = datetime(year, month, 1)
        total_amount = 0
        end_date = None
        if (start_date.month >= 12):
            end_date = start_date.replace(year=start_date.year + 1 ,month=start_date.month - 11, day=1)
        else:
            end_date = start_date.replace(month=start_date.month + 1, day=1) - timedelta(days=1)
        transactions = OrderTransaction.objects.filter(date__gte=datetime.date(start_date), date__lte=datetime.date(end_date), payee=seller, is_successful=True)
        if transactions:
            total_amount = transactions.aggregate(total_amount=Sum('amount'))["total_amount"]
        

        print(start_date, end_date, total_amount)

        return total_amount

    def post(self, request):
        try:
            seller = Seller.objects.get(user=request.user)
            years_and_months = request.data["months"]
            transactions_dict = {}
            for data in years_and_months:
                total_amount = 0
                year, month = data['year'], data['month']
                transactions_data = self.get_transactions_for_year_and_month(year=year, month=month, seller=seller)
                key = f"{year}-{month}"
                transactions_dict[key] = transactions_data
            return Response(transactions_dict, status=status.HTTP_200_OK)
        except Seller.DoesNotExist:
            return Response({"message" : "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class SalesYearView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            seller = Seller.objects.get(user=request.user)
            years = request.data["years"]
            transactions_dict = {}
            for year in years:
                total_amount = 0
                start_year = datetime(year, 1, 1)
                start_day_of_next_year = datetime(year + 1, 1, 1)
                end_year = start_day_of_next_year - timedelta(days=1)
                transactions = OrderTransaction.objects.filter(date__range=[start_year, end_year], payee=seller, is_successful=True)
                if transactions:
                    total_amount = transactions.aggregate(total_amount=Sum('amount'))["total_amount"]
                    transactions_dict[year] = total_amount
                else:
                    transactions_dict[year] = total_amount
            return Response(transactions_dict, status=status.HTTP_200_OK)
        except Seller.DoesNotExist:
            return Response({"message" : "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SalesReportRetriveView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        try:
            seller = Seller.objects.get(user=request.user)
            sales_report = SalesReport.generate_report(seller=seller)
            sales_report_serializer = SalesReportSerializer(sales_report, many=False)
            return Response(sales_report_serializer.data, status=status.HTTP_200_OK)
        except Seller.DoesNotExist:
            return Response({"message" : "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


class SalesReportTimelimeView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            start_date = request.data["start_date"]
            end_date = request.data["end_date"]
            seller = Seller.objects.get(user=request.user)
            print(request.data)
            sales_report = SalesReport.generate_report_timeline(seller=seller, start_date=start_date, end_date=end_date)
            sales_report_serializer = SalesReportSerializer(sales_report, many=False)
            return Response(sales_report_serializer.data, status=status.HTTP_200_OK)
        except Seller.DoesNotExist:
            return Response({"message" : "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)