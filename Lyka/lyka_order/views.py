from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from .serializers import *
from lyka_cart.models import *
from lyka_customer.models import Customer
from lyka_payment.models import CouponType, CouponUsage
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from uuid import uuid1, uuid4


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
                                                   selling_price=unit.selling_price
                                                   )
            order_item.save()

            order_serializer = OrderSerializer(data={})
            order_serializer.is_valid(raise_exception=True)
            order = order_serializer.save()

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
                                                       product_price=item.unit.offer_price, discount=unit.discount, selling_price=unit.selling_price)
                order_item.save()
                order.item = order_item
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

    def patch(self, request, order_id, address_id):
        try:
            customer = Customer.objects.get(user=request.user)
            address = CustomerAddress.objects.get(
                id=address_id, owner=customer)

            if OrderGroup.objects.filter(order_list_id=order_id).exists():
                orders = Order.objects.filter(
                    order_list__order_list_id=order_id)
                for order in orders:
                    order.shipping_address = address
                    order.billing_address = address
                    order.save()
                return Response({"message": "Address updated successfullly"}, status=status.HTTP_200_OK)
            elif Order.objects.filter(order_id=order_id).exists():
                order = Order.objects.get(order_id=order_id)
                order.shipping_address = address
                order.billing_address = address
                order.save()
                return Response({"message": "Address updated successfullly"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        except CustomerAddress.DoesNotExist:
            return Response({"message": "Address not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
                orderlist.total_price = 0
                orderlist.coupon_discount = discount_amount
                orderlist.save()

                for order in orders:
                    order.item.coupon_discount = splited_discount
                    order.item.product_price -= splited_discount
                    order.item.save()
                orderlist.set_total_price()
                orderlist.save()

                return Response({"message": "Coupon has been applied successfully"}, status=status.HTTP_200_OK)

            elif Order.objects.filter(order_id=order_id, customer=customer).exists():
                order = Order.objects.get(order_id=order_id)

                if coupon_usage.usage_count >= coupon.max_usage_limit:
                    return Response({"message": "Coupon usage limit is over"}, status=status.HTTP_400_BAD_REQUEST)

                if not order.total_price >= coupon.minimum_purchase_amount:
                    return Response({"message": f"You have to purchase for the minimum of {coupon.minimum_purchase_amount}"}, status=status.HTTP_400_BAD_REQUEST)

                if not self.is_coupon_valid(coupon=coupon):
                    return Response({"message": "Coupon has been expired"}, status=status.HTTP_400_BAD_REQUEST)

                discount_amount = (
                    (order.total_price * coupon.discount_percentage) / 100)
                if discount_amount > coupon.maximum_discount_amount:
                    discount_amount = coupon.maximum_discount_amount

                order.item.coupon_discount = discount_amount
                order.item.product_price -= discount_amount
                order.item.save()

                return Response({"message": "Coupon has been applied successfully"}, status=status.HTTP_200_OK)

            else:
                return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        except Order.DoesNotExist:
            return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        except Customer.DoesNotExist:
            return Response({"message": "Customer doesn't exist"}, status=status.HTTP_401_UNAUTHORIZED)


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
                return Response({"message": "No more stock left"}, status=status.HTTP_400_BAD_REQUEST)
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
                    order.item.set_selling_price()
                    order.item.save()
                    order.order_status = "Created"
                    order.save()
                orderlist = OrderGroup.objects.get(order_list_id=order_id)
                orderlist.set_total_price()
                orderlist.save()
                orderlist_serializer = OrderGroupPriceSerializer(orderlist, many=False)
                return Response({"type": "multiple", 'price_details' : orderlist_serializer.data}, status=status.HTTP_200_OK)
            elif Order.objects.filter(order_id=order_id, customer=customer).exists():
                order = Order.objects.get(order_id=order_id)
                order.item.set_tax_price()
                order.item.set_selling_price()
                order.item.save()
                order.order_status = "Created"
                order.save()
                order_serializer = OrderItemsPriceSerializer(order.item, many=False)
                return Response({"type": "single", "price_details" : order_serializer.data}, status=status.HTTP_200_OK)
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
                orderlist_serializer = OrderGroupPriceSerializer(orderlist, many=False)
                return Response({"type": "multiple", 'price_details' : orderlist_serializer.data}, status=status.HTTP_200_OK)
            elif Order.objects.filter(order_id=order_id, customer=customer).exists():
                order = Order.objects.get(order_id=order_id)
                order_serializer = OrderItemsPriceSerializer(order.item, many=False)
                return Response({"type": "single", "price_details" : order_serializer.data}, status=status.HTTP_200_OK)
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
        if OrderGroup.objects.filter(order_list_id=order_id).exists():
            orderlist = OrderGroup.objects.get(order_list_id=order_id)
            orderlist.delete()
            return Response({"message" : "Order successfully deleted"}, status=status.HTTP_200_OK)
        elif Order.objects.filter(order_id=order_id).exists():
            order = Order.objects.get(order_id=order_id)
            order.delete()
            return Response({"message" : "Order successfully deleted"}, status=status.HTTP_200_OK)
        else:
            return Response({"message" : "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        
