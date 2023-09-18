from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from .serializers import *
from lyka_customer.models import Customer
from lyka_products.models import Unit
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

class AddtoCartView(generics.ListCreateAPIView):
    serializer_class = Cartserializer

    def post(self, request):
        try:
            quantity = request.data["quantity"]
            unit_id = request.data["unit_id"]

            customer = Customer.objects.get(user=request.user)
            unit = Unit.objects.get(unit_id=unit_id)
            cart = None

            if customer.cart is None:
                serializer = self.get_serializer(data={})
                serializer.is_valid(raise_exception=True)
                cart = serializer.save()
                customer.cart = cart
                customer.save()
            else:
                cart = customer.cart
            cartitem = CartItems.objects.create(cart=cart, quantity=quantity, unit=unit)
            cartitem.item_set()
            cartitem.save()

            return Response("Product added to cart successfully", status=status.HTTP_201_CREATED)
        
        except KeyError:
            return Response("Invalid data. 'Product_id' or 'quantity' is missing.", status=status.HTTP_400_BAD_REQUEST)
        
        except Customer.DoesNotExist:
            return Response("Customer not found.", status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response(str(e), status=status.HTTP_401_UNAUTHORIZED)
        

class RetriveCartView(generics.ListAPIView):
    serializer_class = CartItemsSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def get(self, request, *args, **kwargs):
        try:
            customer = Customer.objects.get(user=request.user)
            if customer.cart is not None:
                cart = customer.cart
                try:
                    cartitems = CartItems.objects.filter(cart=cart)
                    serializer = CartItemsSerializer(cartitems, many=True)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                except CartItems.DoesNotExist:
                    return Response("Cart is Empty", status=status.HTTP_404_NOT_FOUND)
            else:
                return Response("Cart is not Created", status=status.HTTP_400_BAD_REQUEST)
        except Customer.DoesNotExist:
            return Response("Customer not found", status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        

class IncrementCartView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def patch(self, request, cart_item_id, *args, **kwargs):
        try:
            customer = Customer.objects.get(user=request.user)
            if customer.cart is not None:
                cart = customer.cart
                cart_item = CartItems.objects.get(cart=cart, id=cart_item_id)
                if cart_item.quantity >= cart_item.unit.stock:
                    return Response({"message":"Cannot increase quantity, Item out of stock"}, status=status.HTTP_406_NOT_ACCEPTABLE)
                cart_item.quantity += 1
                cart_item.item_set()
                cart_item.save()
                return Response({"message" : f'The quality of {cart_item.unit.product.brand} {cart_item.unit.product.name} has been increased by one'}, status=status.HTTP_200_OK)
            else:
                return Response({"message" : "Cart Doesn't Exist"}, status=status.HTTP_400_BAD_REQUEST)
        except Customer.DoesNotExist:
            return Response({"message" : "Customer authentication failed"}, status=status.HTTP_401_UNAUTHORIZED)
        except CartItems.DoesNotExist:
            return Response({"message" : "Item doesn't exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        

class DecrementCartView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def patch(self, request, cart_item_id):
        try:
            customer = Customer.objects.get(user=request.user)
            if customer.cart is not None:
                cart = customer.cart
                cart_item = CartItems.objects.get(cart=cart, id=cart_item_id)
                if cart_item.quantity > 1:
                    cart_item.quantity -= 1
                    cart_item.item_set()
                    cart_item.save()
                    return Response({"message" : f'The quality of {cart_item.unit.product.brand} {cart_item.unit.product.name} has been decreased by one'}, status=status.HTTP_200_OK)
                elif cart_item.quantity == 1:
                    return Response({"message" : "Cannot decrease the quantity"}, status=status.HTTP_406_NOT_ACCEPTABLE)
            else:
                return Response({"message" : "Cart Doesn't Exist"}, status=status.HTTP_400_BAD_REQUEST)
        except Customer.DoesNotExist:
            return Response({"message" : "Customer authentication failed"}, status=status.HTTP_401_UNAUTHORIZED)
        except CartItems.DoesNotExist:
            return Response({"message" : "Item doesn't exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class DeleteCartItemView(APIView):
    def delete(self, request, cart_item_id):
        try:
            customer = Customer.objects.get(user=request.user)
            if customer.cart is not None:
                cart = customer.cart
                cart_item = CartItems.objects.get(cart=cart, id=cart_item_id)
                cart_item.delete()
                return Response({"message" : f'{cart_item.unit.product.brand} {cart_item.unit.product.name} has been successfully removed from cart'}, status=status.HTTP_200_OK)
            else:
                return Response({"message" : "Cart doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
        except Customer.DoesNotExist:
            return Response({"message" : "Customer Authentication Failed"}, status=status.HTTP_401_UNAUTHORIZED)
        except CartItems.DoesNotExist:
            return Response({"message" : "Item doesn't exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class ItemInCartOrNotView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def get(self, request, unit_id):
        try:
            user = request.user
            customer = Customer.objects.get(user=request.user)
            if customer.cart is None:
                return Response({"message" : "Item doesn't exist"}, status=status.HTTP_200_OK)

            cart_items = CartItems.objects.filter(cart=customer.cart)
            if not cart_items:
                return Response({"message" : "Item doesn't exist"}, status=status.HTTP_200_OK)
            for item in cart_items:
                if item.unit.unit_id == unit_id:
                    return Response({"message" : "Item already in cart"}, status=status.HTTP_400_BAD_REQUEST)
                
            return Response({"message" : "Item doesn't exist"}, status=status.HTTP_200_OK)
        except Customer.DoesNotExist:
            return Response({"message" : "Customer doesn't exist"}, status=status.HTTP_401_UNAUTHORIZED)
        except CartItems.DoesNotExist:
            return Response({"message" : "Item not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class IsCartExistsOrNot(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def get(self, request):
        try:
            customer = Customer.objects.get(user=request.user)
            if customer.cart is None or not CartItems.objects.filter(cart = customer.cart).exists():
                return Response({"message" : "Cart is empty"}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"message" : "Cart is not empty"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



            



