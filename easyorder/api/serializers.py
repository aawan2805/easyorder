from panel.models import *
from rest_framework import serializers


class PlatosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = '__all__'


class ListCategoryByUuid(serializers.Serializer):
    key = serializers.UUIDField()
    icon = serializers.CharField(max_length=200)
    label = serializers.CharField(max_length=200)

# class listcategorybyuuid(serializers.ModelSerializer):
#     class Meta:
#         model = Category
#         fields = '__all__'
