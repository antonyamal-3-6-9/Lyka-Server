from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from .serializers import *
from lyka_cart.models import *
from lyka_customer.models import Customer
from lyka_seller.models import Seller, PickupStore
from lyka_payment.models import CouponType, CouponUsage, OrderTransaction, Wallet
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from uuid import uuid1, uuid4
from django.db.models import Q
import math
import random
import string
import time
import requests
from datetime import date, datetime, timedelta
from lyka_user.models import LykaUser


def convert_to_nested_dict(query_dict):
    nested_data = {}

    def add_to_nested_dict(current_dict, keys, value):
        if len(keys) == 1:
            current_dict[keys[0]] = value
        else:
            key = keys.pop(0)
            if key.endswith(']'):
                key = key[:-1]
            if key not in current_dict:
                current_dict[key] = {}
            add_to_nested_dict(current_dict[key], keys, value)

    for key, value in query_dict.items():
        keys = key.split('[')
        keys = [k[:-1] if k.endswith(']') else k for k in keys]
        add_to_nested_dict(nested_data, keys, value)

    return nested_data


class DirectOrderCreateView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            quantity = request.data.get("quantity")
            unit_id = request.data.get("unit_id")

            if not unit_id or not quantity:
                return Response({"message": "Unit ID and quantity are required."}, status=status.HTTP_400_BAD_REQUEST)

            customer = Customer.objects.get(user=request.user)
            unit = Unit.objects.get(unit_id=unit_id)

            order_item = OrderItems.objects.create(product=unit.product, quantity=quantity, product_color=unit.color_code,
                                                   product_variant=unit.variant, product_price=unit.offer_price, discount=unit.discount,
                                                   selling_price=unit.selling_price, original_price=unit.original_price
                                                   )
            order_item.save()

            order_serializer = OrderSerializer(data={})
            order_serializer.is_valid(raise_exception=True)
            order = order_serializer.save()

            order.pickup_address = unit.warehouse.store_address
            order.item = order_item
            order.customer = customer
            order.seller = unit.seller
            order.save()

            return Response(order_serializer.data, status=status.HTTP_201_CREATED)
        except Unit.DoesNotExist:
            return Response({"message": "Product does not exist."}, status=status.HTTP_404_NOT_FOUND)
        except Customer.DoesNotExist:
            return Response({"message": "Customer does not exist."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CartCreateOrderView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            i = 1
            customer = Customer.objects.get(user=request.user)
            items = CartItems.objects.filter(cart=customer.cart)

            order_list = OrderGroup.objects.create(order_list_id=uuid4())

            for item in items:
                unit = Unit.objects.get(unit_id=item.unit.unit_id)
                order = Order.objects.create(
                    order_id=uuid1(), order_list=order_list)

                order_item = OrderItems.objects.create(product=item.unit.product, quantity=item.quantity,
                                                       product_variant=item.unit.variant, product_color=item.unit.color_code,
                                                       product_price=item.unit.offer_price, discount=unit.discount, selling_price=unit.selling_price, original_price=unit.original_price)
                order_item.save()
                order.item = order_item
                order.pickup_address = unit.warehouse.store_address
                order.customer = customer
                order.seller = item.unit.seller
                order.save()
                order_list.order_count = i
                order_list.save()
                i += 1
            order_list.set_total_price()
            order_list.save()
            return Response(order_list.order_list_id, status=status.HTTP_201_CREATED)
        except Customer.DoesNotExist:
            return Response({"message": "Customer does not exist."}, status=status.HTTP_404_NOT_FOUND)
        except Cart.DoesNotExist:
            return Response({"message": "Cart does not exist."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderAddressUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def geocode_postal_code(self, postal_code):
        base_url = "https://nominatim.openstreetmap.org/search"
        params = {
            "postalcode": postal_code,
            "format": "json",
        }

        response = requests.get(base_url, params=params)
        data = response.json()

        if data:
            latitude = float(data[0]["lat"])
            longitude = float(data[0]["lon"])
            return latitude, longitude
        else:
            return None, None

    def haversine_distance(self, lat1, lon1, lat2, lon2):

        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * \
            math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        R = 6371.0

        distance = R * c
        return distance

    def calculate_shipping_charge(self, postal_code_one, postal_code_two):
        lat1, lon1 = self. geocode_postal_code(postal_code_one)
        lat2, lon2 = self.geocode_postal_code(postal_code_two)
        distance = self.haversine_distance(
            lat1=lat1, lat2=lat2, lon1=lon1, lon2=lon2)
        shipping_charge = int(distance) * 0.2
        return shipping_charge

    def patch(self, request, order_id, address_id):
        try:
            customer = Customer.objects.get(user=request.user)
            address = CustomerAddress.objects.get(
                id=address_id, owner=customer)

            if OrderGroup.objects.filter(order_list_id=order_id).exists():
                orderlist = OrderGroup.objects.get(order_list_id=order_id)
                orders = Order.objects.filter(
                    order_list__order_list_id=order_id)
                for order in orders:
                    if order.shipping_address:
                        if order.shipping_address == address:
                            pass
                        else:
                            shipping_charge = self.calculate_shipping_charge(
                                address.zip_code, order.pickup_address.zip_code)
                            order.item.product_price -= order.shipping_charge
                            order.item.save()
                            order.shipping_address = address
                            order.billing_address = address
                            order.shipping_charge = shipping_charge
                            order.save()
                            order.item.product_price += order.shipping_charge
                            order.item.save()
                    else:
                        shipping_charge = self.calculate_shipping_charge(
                            address.zip_code, order.pickup_address.zip_code)
                        order.shipping_address = address
                        order.billing_address = address
                        order.shipping_charge = shipping_charge
                        order.save()
                        order.item.product_price += shipping_charge
                        order.item.save()
                    orderlist.set_total_price()
                    orderlist.save()
                return Response({"message": "Address updated successfullly"}, status=status.HTTP_200_OK)
            elif Order.objects.filter(order_id=order_id).exists():
                order = Order.objects.get(order_id=order_id)
                if order.shipping_address:
                    if order.shipping_address == address:
                        return Response({"message": "Address updated successfullly"}, status=status.HTTP_200_OK)
                    else:
                        shipping_charge = self.calculate_shipping_charge(
                            address.zip_code, order.pickup_address.zip_code)
                        order.item.product_price -= order.shipping_charge
                        order.item.save()
                        order.shipping_address = address
                        order.billing_address = address
                        order.shipping_charge = shipping_charge
                        order.save()
                        order.item.product_price += order.shipping_charge
                        order.item.save()
                else:
                    shipping_charge = self.calculate_shipping_charge(
                        address.zip_code, order.pickup_address.zip_code)
                    order.shipping_address = address
                    order.billing_address = address
                    order.shipping_charge = shipping_charge
                    order.save()
                    order.item.product_price += shipping_charge
                    order.item.save()
                return Response({"message": "Address updated successfullly"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        except CustomerAddress.DoesNotExist:
            return Response({"message": "Address not found"}, status=status.HTTP_404_NOT_FOUND)
        # except Exception as e:
        #     return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderApplyCoupon(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def is_coupon_valid(self, coupon):
        current_datetime = timezone.now()
        return coupon.start_date <= current_datetime <= coupon.end_date

    def split_discount(self, discount, count):
        return discount / count

    def post(self, request):
        try:
            user = request.user
            customer = Customer.objects.get(user=user)
            coupon_code = request.data["coupon_code"]
            order_id = request.data["order_id"]
            coupon = get_object_or_404(CouponType, code=coupon_code)
            coupon_usage, _ = CouponUsage.objects.get_or_create(
                customer=customer, coupon_type=coupon)

            if OrderGroup.objects.filter(order_list_id=order_id).exists():
                if coupon_usage.usage_count >= coupon.max_usage_limit:
                    return Response({"message": "Coupon usage limit is over"}, status=status.HTTP_400_BAD_REQUEST)

                orderlist = get_object_or_404(
                    OrderGroup, order_list_id=order_id)
                if orderlist.applied_coupon:
                    return Response({"message": "Already applied"}, status=status.HTTP_406_NOT_ACCEPTABLE)
                orders = Order.objects.filter(
                    order_list=orderlist, customer=customer)

                if not orderlist.total_price >= coupon.minimum_purchase_amount:
                    return Response({"message": f"You have to purchase for the minimum of {coupon.minimum_purchase_amount}"}, status=status.HTTP_400_BAD_REQUEST)

                if not self.is_coupon_valid(coupon=coupon):
                    return Response({"message": "Coupon has been expired"}, status=status.HTTP_400_BAD_REQUEST)

                discount_amount = (
                    (orderlist.total_price * coupon.discount_percentage) / 100)
                if discount_amount > coupon.maximum_discount_amount:
                    discount_amount = coupon.maximum_discount_amount

                splited_discount = self.split_discount(
                    discount_amount, orderlist.order_count)

                for order in orders:
                    order.item.coupon_discount += splited_discount
                    order.item.product_price -= splited_discount
                    order.item.save()
                    order.applied_coupon = coupon
                    order.save()
                orderlist.applied_coupon = coupon
                orderlist.set_total_price()
                orderlist.save()
                coupon_usage.usage_count += 1
                coupon_usage.save()

                return Response({"message": "Coupon has been applied successfully", 'coupon_discount': orderlist.coupon_discount, 'total_price': orderlist.total_price}, status=status.HTTP_200_OK)

            elif Order.objects.filter(order_id=order_id, customer=customer).exists():
                order = Order.objects.get(order_id=order_id)
                if order.applied_coupon:
                    return Response({"message": "Already applied"}, status=status.HTTP_406_NOT_ACCEPTABLE)

                if coupon_usage.usage_count >= coupon.max_usage_limit:
                    return Response({"message": "Coupon usage limit is over"}, status=status.HTTP_400_BAD_REQUEST)

                if not order.item.product_price >= coupon.minimum_purchase_amount:
                    return Response({"message": f"You have to purchase for the minimum of {coupon.minimum_purchase_amount}"}, status=status.HTTP_400_BAD_REQUEST)

                if not self.is_coupon_valid(coupon=coupon):
                    return Response({"message": "Coupon has been expired"}, status=status.HTTP_400_BAD_REQUEST)

                discount_amount = (
                    (order.item.product_price * coupon.discount_percentage) / 100)
                if discount_amount > coupon.maximum_discount_amount:
                    discount_amount = coupon.maximum_discount_amount

                order.item.coupon_discount += discount_amount
                order.item.product_price -= discount_amount
                order.item.save()
                order.applied_coupon = coupon
                order.save()

                coupon_usage.usage_count += 1
                coupon_usage.save()

                return Response({"message": "Coupon has been applied successfully", 'coupon_discount': order.item.coupon_discount, 'total_price': order.item.product_price}, status=status.HTTP_200_OK)

            else:
                return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        except Order.DoesNotExist:
            return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        except Customer.DoesNotExist:
            return Response({"message": "Customer doesn't exist"}, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderItemIncrementView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def patch(self, request, order_id):
        try:
            customer = Customer.objects.get(user=request.user)
            order = Order.objects.get(order_id=order_id, customer=customer)

            unit = Unit.objects.get(product=order.item.product, variant=order.item.product_variant,
                                    color_code=order.item.product_color, seller=order.seller)

            old_quantity = order.item.quantity
            if unit.stock <= order.item.quantity:
                return Response({"message": "No more stock left"}, status=status.HTTP_400_BAD_REQUEST)
            new_quantity = int(old_quantity) + 1
            order.item.quantity = new_quantity
            order.item.save()
            order.save()
            return Response({"message": "Successfully increased the quantity"}, status=status.HTTP_200_OK)
        except Customer.DoesNotExist:
            return Response({"message": "Authentication failed"}, status=status.HTTP_401_UNAUTHORIZED)
        except Order.DoesNotExist:
            return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderItemDecrementView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def patch(self, request, order_id):
        try:
            customer = Customer.objects.get(user=request.user)
            order = Order.objects.get(order_id=order_id, customer=customer)
            old_quantity = order.item.quantity
            if order.item.quantity <= 1:
                return Response({"message": "Cannot decrease the quantity anymore"}, status=status.HTTP_400_BAD_REQUEST)
            new_quantity = int(old_quantity) - 1
            order.item.quantity = new_quantity
            order.item.save()
            order.save()
            return Response({"message": "Successfully decreased the quantity"}, status=status.HTTP_200_OK)
        except Customer.DoesNotExist:
            return Response({"message": "Authentication failed"}, status=status.HTTP_401_UNAUTHORIZED)
        except Order.DoesNotExist:
            return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderItemsConfirmationView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def patch(self, request, order_id):
        try:
            customer = Customer.objects.get(user=request.user)
            if OrderGroup.objects.filter(order_list_id=order_id).exists():
                orders = Order.objects.filter(
                    order_list__order_list_id=order_id, customer=customer)
                for order in orders:
                    order.item.set_tax_price()
                    order.item.save()
                    order.item.set_selling_price()
                    order.item.save()
                    order.status = Order.CREATED
                    order.save()
                orderlist = OrderGroup.objects.get(order_list_id=order_id)
                orderlist.set_total_price()
                orderlist.save()
                return Response({"message": "success"}, status=status.HTTP_200_OK)
            elif Order.objects.filter(order_id=order_id, customer=customer).exists():
                order = Order.objects.get(order_id=order_id)
                order.item.set_tax_price()
                order.item.save()
                order.item.set_selling_price()
                order.item.save()
                order.status = Order.CREATED
                order.save()
                return Response({"message": "success"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        except Customer.DoesNotExist:
            return Response({"message": "Authentication failed"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request, order_id):
        try:
            customer = Customer.objects.get(user=request.user)
            if OrderGroup.objects.filter(order_list_id=order_id).exists():
                orderlist = OrderGroup.objects.get(order_list_id=order_id)
                orderlist_serializer = OrderGroupPriceSerializer(
                    orderlist, many=False)
                return Response({"type": "multiple", 'price_details': orderlist_serializer.data}, status=status.HTTP_200_OK)
            elif Order.objects.filter(order_id=order_id, customer=customer).exists():
                order = Order.objects.get(order_id=order_id)
                order_serializer = OrderPriceSerializer(
                    order, many=False)
                return Response({"type": "single", "price_details": order_serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        except Customer.DoesNotExist:
            return Response({"message": "Authentication failed"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderRetriveView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, order_id):
        try:
            customer = Customer.objects.get(user=request.user)
            if OrderGroup.objects.filter(order_list_id=order_id).exists():
                orders = Order.objects.filter(
                    order_list__order_list_id=order_id, customer=customer)
                order_serializer = OrderRetriveSerializer(orders, many=True)
                return Response(order_serializer.data, status=status.HTTP_200_OK)
            elif Order.objects.filter(order_id=order_id, customer=customer).exists():
                order = Order.objects.get(order_id=order_id)
                order_serializer = OrderRetriveSerializer(order, many=False)
                return Response(order_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        except Customer.DoesNotExist:
            return Response({"message": "Authentication failed"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CancelOrderView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def delete(self, request, order_id):
        customer = Customer.objects.get(user=request.user)
        if OrderGroup.objects.filter(order_list_id=order_id).exists():
            orderlist = OrderGroup.objects.get(order_list_id=order_id)
            if orderlist.applied_coupon:
                coupon_usage = CouponUsage.objects.get(
                    coupon_type=orderlist.applied_coupon, customer=customer)
                coupon_usage.usage_count -= 1
                coupon_usage.save()
            orderlist.delete()
            return Response({"message": "Order successfully deleted"}, status=status.HTTP_200_OK)
        elif Order.objects.filter(order_id=order_id).exists():
            order = Order.objects.get(order_id=order_id)
            if order.applied_coupon:
                coupon_usage = CouponUsage.objects.get(
                    coupon_type=order.applied_coupon, customer=customer)
                coupon_usage.usage_count -= 1
                coupon_usage.save()
            order.delete()
            return Response({"message": "Order successfully deleted"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)


class SellerOrderListView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        try:
            seller = Seller.objects.get(user=request.user)
            orders = Order.objects.filter(
                seller=seller
            ).exclude(
                status=Order.CREATED
            )
            order_serializer = OrderRetriveSerializer(orders, many=True)
            if not orders:
                return Response({"message": "No orders"}, status=status.HTTP_404_NOT_FOUND)
            return Response(order_serializer.data, status=status.HTTP_200_OK)
        except Seller.DoesNotExist:
            return Response({"message": "Seller not found"}, status=status.HTTP_404_NOT_FOUND)
        except Order.DoesNotExist:
            return Response({"message": "No Orders"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderAcceptOrReject(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def generate_unique_tracking_number(self):
        prefix = "LYKA"
        random_string = ''.join(random.choices(
            string.ascii_uppercase + string.digits, k=6))
        timestamp = int(time.time())
        unique_tracking_number = f"{prefix}-{random_string}-{timestamp}"
        return unique_tracking_number

    def patch(self, request):
        try:
            order_id = request.data["order_id"]
            order_status = request.data["status"]
            seller = Seller.objects.get(user=request.user)
            order = Order.objects.get(order_id=order_id, seller=seller)
            print(request.data)
            if order_status == "Accepted":
                order.status = Order.CONFIRMED
                order.credentials.tracking_id = self.generate_unique_tracking_number()
                order.credentials.save()
                order.time = timezone.now()
                order.delivery_date = date.today()
            else:
                order.status = Order.REJECTED
                unit = Unit.objects.get(variant=order.item.product_variant,
                            color_code=order.item.product_color, product=order.item.product, seller=order.seller)
                old_stock = unit.stock
                new_stock = int(old_stock) + int(order.item.quantity)
                unit.stock = new_stock
                unit.save()
            order.save()
            return Response({"message": "Order status has been updated succesfully"}, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderDetailsRetriveView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, order_id):
        try:
            order = None
            if request.user.role == LykaUser.SELLER:
                order = Order.objects.get(
                    order_id=order_id, seller__user=request.user)
            elif request.user.role == LykaUser.CUSTOMER:
                order = Order.objects.get(
                    order_id=order_id, customer__user=request.user)
            order_serializer = OrderDetailsRetriveSerializer(order, many=False)
            return Response(order_serializer.data, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)


class CustomerOrderListView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        try:
            customer = Customer.objects.get(user=request.user)
            orders = Order.objects.filter(customer=customer).exclude(
                Q(status=None) | Q(status=Order.CREATED)
            )
            order_serializer = OrderRetriveSerializer(orders, many=True)
            if not orders:
                return Response({"message": "No orders"}, status=status.HTTP_404_NOT_FOUND)
            return Response(order_serializer.data, status=status.HTTP_200_OK)
        except Customer.DoesNotExist:
            return Response({"message": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        except Order.DoesNotExist:
            return Response({"message": "No Orders"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomerOrderCancelView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def patch(self, request, order_id):
        try:
            order = Order.objects.get(
                order_id=order_id, customer__user=request.user)
            if order.status != Order.DELIVERED:
                order.status = Order.CANCELATION_REQUESTED
                order.save()
                unit = Unit.objects.get(variant=order.item.product_variant,
                                    color_code=order.item.product_color, product=order.item.product, seller=order.seller)
                unit.stock += order.item.quantity
                unit.save()
                return Response({"message": "order has been successfully cancelled"}, status=status.HTTP_200_OK)
            else:
                return Response({"message" : "Order can't be cancelled, kindly request return"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        except Order.DoesNotExist:
            return Response({"message": "order not found"}, status=status.HTTP_404_NOT_FOUND)
        except Customer.DoesNotExist:
            return Response({"message": "Customer doesn't exist"}, status=status.HTTP_401_UNAUTHORIZED)


class OrderReturnInitiationView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def patch(self, request, order_id):
        try:
            order = Order.objects.get(
                order_id=order_id, customer__user=request.user)
            if order.status == Order.DELIVERED:
                order.status = Order.RETURN_REQUESTED
                order.save()
                return Response({"message": "Return has been requested successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"message" : "Order can't be returned, kindly request for cancellation"}, status=status.HTTP_406_NOT_ACCEPTABLE )
        except Order.DoesNotExist:
            return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
