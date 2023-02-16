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


class OrderDishes(serializers.Serializer):
    dish_uuid = serializers.UUIDField()
    quantity = serializers.IntegerField()


class PostNewOrder(serializers.Serializer):
    dishes = serializers.ListField(child=
        serializers.ListField(
            child = OrderDishes()
        )
    )
    brand_uuid = serializers.UUIDField()

# class listcategorybyuuid(serializers.ModelSerializer):
#     class Meta:
#         model = Category
#         fields = '__all__'
