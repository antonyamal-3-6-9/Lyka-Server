from rest_framework import serializers
from .models import *
import uuid
from django.utils.text import slugify
from lyka_products.models import Details

class RootSerializer(serializers.ModelSerializer):
    root_id = serializers.UUIDField(read_only=True)
    class Meta:
        model = Root
        fields = ['root_id','name']

    def create(self, validated_data):
        print(validated_data)
        name = validated_data['name']
        slug = slugify(name)
        id = uuid.uuid4()
        root = Root.objects.create(root_id=id, root_slug=slug, **validated_data)
        return root


class MainSerializer(serializers.ModelSerializer):
    root = serializers.PrimaryKeyRelatedField(queryset=Root.objects.all())
    main_id = serializers.UUIDField(read_only=True)
    class Meta:
        model = Main
        fields = ['main_id', "name", "root"]

    def create(self, validated_data):
        name = validated_data['name']
        slug = slugify(name)
        id = uuid.uuid4()
        main = Main.objects.create(main_id=id, main_slug=slug, **validated_data)
        return main


class SubSerializer(serializers.ModelSerializer):
    main = serializers.PrimaryKeyRelatedField(queryset=Main.objects.all())
    sub_id = serializers.UUIDField(read_only=True)
    class Meta:
        model = Sub
        fields = ['sub_id', 'name', 'main']

    def create(self, validated_data):
        name = validated_data['name']
        slug = slugify(name)
        id = uuid.uuid4()
        sub = Sub.objects.create(sub_id=id, sub_slug=slug, **validated_data)
        return sub



class RootViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Root
        fields = "__all__"

class MainViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Main
        fields = "__all__"
    
class SubViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sub
        fields = "__all__"
    

class DetailsRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Details
        fields = "__all__"
        
        
        
