import base64
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
import requests
from .signals import order_placed
from rest_framework import generics
from lyka_customer.models import Customer
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


def generate_unique_payment_id():
    timestamp = int(time.time() * 1000) 
    random_string = secrets.token_hex(4).upper()
    payment_id = f'{timestamp}{random_string}'
    return payment_id


def update_order(lyka_order_id, payment_method):
    if OrderGroup.objects.filter(order_list_id=lyka_order_id).exists():
        orders = Order.objects.filter(order_list__order_list_id=lyka_order_id)
        for order in orders:
            order.payment_method = payment_method
            order.payment_status = True
            order.order_status = "Placed"
            order.save()
            unit = Unit.objects.get(variant=order.item.product_variant,
                                    color_code=order.item.product_color, product=order.item.product, seller=order.seller)
            order_placed.send(sender=order.customer, unit=unit,
                         quantity=order.item.quantity)
        return True
    elif Order.objects.filter(order_id=lyka_order_id).exists():
        order = Order.objects.get(order_id=lyka_order_id)
        order.payment_method = payment_method
        order.payment_status = True
        order.order_status = "Placed"
        order.save()
        unit = Unit.objects.get(variant=order.item.product_variant,
                                color_code=order.item.product_color, product=order.item.product, seller=order.seller)
        order_placed.send(sender=order.customer, unit=unit,
                     quantity=order.item.quantity)
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
                        return Response({"message": "payment successfull and order has been placed"}, status=status.HTTP_200_OK)
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
                print(e)
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


# if Order.objects.filter(order_list_id=lyka_order_id).exists():
#                             orders = Order.objects.filter(order_list__order_list_id=lyka_order_id, customer=customer)
#                             for order in orders:
#                                 serializer = TransactionSerializer(data={})
#                                 serializer.is_valid(raise_exception=True)
#                                 transaction = serializer.save()
#                                 transaction.payer = customer
#                                 transaction.payee = order.seller
#                                 transaction.wallet = order.seller.wallet
#                                 transaction.order = order
#                                 transaction.entry = "Credit"
#                                 transaction.amount = order.item.item_price
#                                 transaction.is_successful = True
#                                 transaction.save()
#                                 order.seller.wallet.wallet_amount += transaction.amount
#                                 order.seller.wallet.save()
#                                 order.status = "Placed"
#                                 order.payment = True
#                                 order.credentials.payment_id = transaction.ref_no
#                                 order.save()
#                             return Response({"message" : "payment successfull"}, status=status.HTTP_200_OK)
#                         elif Order.objects.filter(order_id=lyka_order_id, customer=customer).exists():
#                             order = Order.objects.get(order_id=lyka_order_id, customer=customer)
#                             serializer = TransactionSerializer(data={})
#                             serializer.is_valid(raise_exception=True)
#                             transaction = serializer.save()
#                             transaction.payer = customer
#                             transaction.payee = order.seller
#                             transaction.wallet = order.seller.wallet
#                             transaction.order = order
#                             transaction.entry = "Credit"
#                             transaction.amount = order.item.item_price
#                             transaction.is_successful = True
#                             transaction.save()
#                             order.seller.wallet.wallet_amount += transaction.amount
#                             order.seller.wallet.save()
#                             order.status = "Placed"
#                             order.payment = True
#                             order.credentials.payment_id = transaction.ref_no
#                             order.save()
