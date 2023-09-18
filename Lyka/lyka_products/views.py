from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import *
from .models import *
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q


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


class ProductCreateView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def post(self, request):
        try:
            images_data = request.data.pop('images[]')
            colors_data = request.data.pop('colors[]')
            variations_data = request.data.pop('variations[]')

            data = convert_to_nested_dict(request.data)
            product_data = data['product']
            details_data = data['details']

            product_serializer = ProductAddSerializer(data=product_data)
            product_serializer.is_valid(raise_exception=True)
            product = product_serializer.save()

            details_serializer = PDetailsSerializer(data=details_data)
            details_serializer.is_valid(raise_exception=True)
            details = details_serializer.save()

            product.details = details
            product.save()

            for color_data in colors_data:
                color, created = Color.objects.get_or_create(color=color_data)
                product.colors.add(color)

            for variation_data in variations_data:
                variation, created = Variations.objects.get_or_create(variation=variation_data)
                product.variations.add(variation)

            for image_data in images_data:
                image, created = ProductImage.objects.get_or_create(image=image_data)
                product.images.add(image)

            return Response({"message": "Product created successfully.","product" : product_serializer.data}, status=status.HTTP_201_CREATED)
        except KeyError as e:
            return Response({"message" : str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LykaUnitCreateView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def post(self, request):
        try:
            user = request.user
            units_data = request.data.pop('units')
            seller = Seller.objects.get(user=user)
            existing_units_messages = []

            for unit_data in units_data:
                if Unit.objects.filter(product__productId=unit_data["product"], variant__id=unit_data["variant"], color_code=unit_data["color_code"], seller=seller).exists():
                    existing_units_messages.append(f"A unit with the same data already exists: {unit_data}")
                else:
                    unit_serializer = UnitCreateSerializer(data=unit_data)
                    unit_serializer.is_valid(raise_exception=True)
                    unit = unit_serializer.save()
                    unit.seller = seller
                    unit.set_slug()
                    unit.set_discount()
                    unit.save()
            if existing_units_messages:
                return Response(existing_units_messages, status=status.HTTP_200_OK)
            else:
                return Response({"message" : "Item created sucessfully"}, status=status.HTTP_200_OK)
        except Seller.DoesNotExist:
            return Response({"message" : "Seller doesn't exists"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProductVariationGetView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def get(self, request, pk):
        try:
            product = Product.objects.get(productId=pk)
            variations = product.variations.all()
            colors = product.colors.all()

            variation_serializer = VariationsSerializer(variations, many=True)
            color_serializer = ColorSerializer(colors, many=True)
            return Response({"variations" : variation_serializer.data, "colors" : color_serializer.data}, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({"message" : "Product doesnot exist"}, status=status.HTTP_404_NOT_FOUND)
        except Variations.DoesNotExist:
            return Response({"message" : "Variantions doesnot exist"}, status=status.HTTP_404_NOT_FOUND)
        except Color.DoesNotExist:
            return Response({"message" : "Colors doesnot exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_400_BAD_REQUEST)



class ProductCheckView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def get(self, request):
        try:
            brand = request.query_params.get('brand')
            name = request.query_params.get('name')
            main = request.query_params.get('main')
            root = request.query_params.get('root')
            sub = request.query_params.get('sub')

            main_category = Main.objects.get(main_id = main)
            root_category = Root.objects.get(root_id = root)
            sub_category = Sub.objects.get(sub_id = sub)

            products = Product.objects.filter(
                Q(root_category=root_category) &
                Q(main_category=main_category) &
                Q(sub_category=sub_category) &
                Q(brand__icontains=brand) &
                Q(name__icontains=name)
            )

            if not products:
                return Response({"message" : "Product not found"}, status=status.HTTP_404_NOT_FOUND)

            product_serializer = ProductRetriveSerializer(products, many=True)
            return Response(product_serializer.data, status=status.HTTP_200_OK)

        except Main.DoesNotExist:
            return Response({"message" : "Main Category doesnot exist"}, status=status.HTTP_404_NOT_FOUND)
        except Root.DoesNotExist:
            return Response({"message" : "Root Category doesn't exist"}, status=status.HTTP_404_NOT_FOUND)
        except Sub.DoesNotExist:
            return Response({"message" : "Sub Category doesn't exist"}, status=status.HTTP_404_NOT_FOUND)
        except Product.DoesNotExist:
            return Response({"message" : "Product doesnot exist"}, status=status.HTTP_404_NOT_FOUND)
        except KeyError as e:
            return Response({"message" : str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ImageUploadView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def post(self, request, product_id):
        user = request.user
        seller = get_object_or_404(Seller, user=user)
        product = get_object_or_404(Product, pk=product_id, seller=seller)
        serializer = ImageSerializer(data=request.data, context={'product': product})
        
        if serializer.is_valid():
            serializer.save(product=product)
            return Response("Image Has been added successfully", status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailsAddView(generics.UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductAddDetailsSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def update(self, request, *args, **kwargs):
        try:
            user = self.request.user
            seller = Seller.objects.get(user=user)
            p_id = request.data.get("product_id")
            print(p_id)
            nested_data = convert_to_nested_dict(request.data)
            product = Product.objects.get(productId=p_id, seller=seller)
            if product.details is not None:
                product.details.delete()
            serializer = self.get_serializer(product, data=nested_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Seller.DoesNotExist:
            return Response({"error": "Seller does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Product.DoesNotExist:
            return Response({"error": "Product does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ShowDetailsView(APIView):
    def get(self, request):
        main = request.query_params.get("main")
        try:
            main_category = Main.objects.get(main_id=main)
            details = Details.objects.get(product_type=main_category)
            data = PDetailsSerializer(details, many=False)
            return Response(data.data)
        except Main.DoesNotExist:
            return Response("Details not found", status=status.HTTP_404_NOT_FOUND)

        
class UnitListView(generics.ListAPIView):
    queryset = Unit.objects.all()
    serializer_class = UnitRetriveSerializer

    def get(self, request, *args, **kwargs):
        try:
            items = Unit.objects.filter(is_active=True)
            item_serializer = self.get_serializer(items, many=True)
            return Response(item_serializer.data, status=status.HTTP_200_OK)
        except Unit.DoesNotExist:
            return Response({"message" : "Error getting units"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LykaItemRootCategoryRetriveView(APIView):
    def get(self, request):
        root = request.query_params.get("root")
        try:
            items = Unit.objects.filter(product__root_category__root_id=root)
            serializer = UnitRetriveSerializer(items, many=True)
            return Response(serializer.data)
        except Unit.DoesNotExist:
            return Response("Items not found", status=status.HTTP_404_NOT_FOUND)

class LykaItemMainCategoryRetriveView(APIView):
    def get (self, request):
        main = request.query_params.get('main')
        try:
            items = Unit.objects.filter(product__main_category__main_main_id=main)
            data = UnitRetriveSerializer(items, many=True)
            return Response(data.data)
        except Product.DoesNotExist:
            return Response("Product not found", status=status.HTTP_404_NOT_FOUND)
        

class LykaItemSubCategoryRetriveView(APIView):
    def get (self, request):
        sub = request.query_params.get('sub')
        try:
            items = Unit.objects.filter(product__sub_category__sub_id=sub)
            data = UnitRetriveSerializer(items, many=True)
            return Response(data.data)
        except Product.DoesNotExist:
            return Response("Product not found", status=status.HTTP_404_NOT_FOUND)
        

class ItemSellerListView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def get(self, request):
        try:
            seller = get_object_or_404(Seller, user=request.user)
            items = Unit.objects.filter(seller=seller)

            if not items:
                return Response({"message": "No products found"}, status=status.HTTP_404_NOT_FOUND)

            serializer = UnitRetriveSerializer(items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class ItemMakeLiveView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def patch(self, request):
        unit_id = request.data["unit_id"]
        try:
            user = request.user
            unit = Unit.objects.get(unit_id=unit_id)

            if unit.is_active:
                unit.is_active = False
                unit.save()
                if not unit.is_active:
                    return Response({"message" : "Dead"}, status=status.HTTP_200_OK)
                else:
                    return Response({"message" : "Live"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                unit.is_active = True
                unit.save()
                if unit.is_active:
                    return Response({"message" : "Live"}, status=status.HTTP_200_OK)
                else:
                    return Response({"message" : "Dead"}, status=status.HTTP_400_BAD_REQUEST)
                    
        except Unit.DoesNotExist:
            return Response({"message" : "Item doesnot exist"}, status=status.HTTP_404_NOT_FOUND)
        except Seller.DoesNotExist:
            return Response({"message" : "Seller doesn't exist"}, status=status.HTTP_401_UNAUTHORIZED)
        except Unit.DoesNotExist:
            return Response({"message" : "Variant doesnot exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ItemVariantDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def delete(self, request, unit_id):
        user = request.user
        seller = get_object_or_404(Seller, user=user)
        try:
            unit = Unit.objects.get(unit_id=unit_id)
            unit.delete()
            return Response({"message": "Variant deleted successfully"}, status=status.HTTP_200_OK)
        except Unit.DoesNotExist:
            return Response({"message": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        except Unit.DoesNotExist:
            return Response({"message": "Variant not found."}, status=status.HTTP_404_NOT_FOUND)



class ItemAddMoreStockView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def patch(self, request):
        try:
            unit_id = request.data["unit_id"]
            new_stock = request.data["stock"]
            user = request.user
            seller = Seller.objects.get(user=user)
            unit = Unit.objects.get(unit_id=unit_id)
            stock = unit.stock
            stock += int(new_stock)
            unit.stock = stock
            unit.save()
            return Response({"message" : "Stock has been added successfully"}, status=status.HTTP_200_OK)
        except Seller.DoesNotExist:
            return Response({"message" : "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        except Product.DoesNotExist:
            return Response({"message" : "Productr does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class ItemRetriveView(APIView):
    def get(self, request, unit_id):
        try:
            item = Unit.objects.get(unit_id = unit_id)
            item_serializer = UnitDetailsRetriveSerializer(item, many=False)
            return Response(item_serializer.data, status=status.HTTP_200_OK)
        
        except Unit.DoesNotExist:
            return Response({"message": "Product does not exist"}, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ColorOrVariantExistsView(APIView):
    def get(self, request, seller_id, product_id, color_id, variant_id, is_variant_color):
        try:
            if Unit.objects.filter(color_code__id=color_id, seller__unique_id=seller_id, product__productId=product_id, variant__id=variant_id).exists():
                unit = Unit.objects.filter(color_code__id=color_id, seller__unique_id=seller_id, product__productId=product_id, variant__id=variant_id).first()
                unit_serializer = UnitDetailsRetriveSerializer(unit, many=False)
                return Response(unit_serializer.data, status=status.HTTP_200_OK)
            elif Unit.objects.filter(color_code__id=color_id, product__productId=product_id, variant__id=variant_id).exists():
                unit = Unit.objects.filter(color_code__id=color_id, product__productId=product_id, variant__id=variant_id).first()
                unit_serializer = UnitDetailsRetriveSerializer(unit, many=False)
                return Response(unit_serializer.data, status=status.HTTP_200_OK)
            
            if is_variant_color == "color":
                if Unit.objects.filter(color_code__id=color_id, product__productId=product_id, seller=seller_id).exists():
                    unit = Unit.objects.filter(color_code__id=color_id, product__productId=product_id, seller=seller_id).first()
                    unit_serializer = UnitDetailsRetriveSerializer(unit, many=False)
                    return Response(unit_serializer.data, status=status.HTTP_200_OK)
                elif Unit.objects.filter(color_code__id=color_id, product__productId=product_id).exists():
                    unit = Unit.objects.filter(color_code__id=color_id, product__productId=product_id).first()
                    unit_serializer = UnitDetailsRetriveSerializer(unit, many=False)
                    return Response(unit_serializer.data, status=status.HTTP_200_OK)
            elif is_variant_color == "variant":
                if Unit.objects.filter(variant__id=variant_id, product__productId=product_id, seller=seller_id).exists():
                    unit = Unit.objects.filter(variant__id=variant_id, product__productId=product_id, seller=seller_id).first()
                    unit_serializer = UnitDetailsRetriveSerializer(unit, many=False)
                    return Response(unit_serializer.data, status=status.HTTP_200_OK)
                elif Unit.objects.filter(variant__id=variant_id, product__productId=product_id).exists():
                    unit = Unit.objects.filter(variant__id=variant_id, product__productId=product_id).first()
                    unit_serializer = UnitDetailsRetriveSerializer(unit, many=False)
                    return Response(unit_serializer.data, status=status.HTTP_200_OK)
                
            color = Color.objects.get(id=color_id)
            variant = Variations.objects.get(id=variant_id)
            return Response(
                            {"message" : f'Not avaialble with given color: {color.color} and variant: {variant.variation}'},
                             status=status.HTTP_404_NOT_FOUND
                            )
        except Exception as e:
            return Response({"message" : str(e)}, status=status.HTTP_400_BAD_REQUEST)

