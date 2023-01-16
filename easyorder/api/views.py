from datetime import datetime

from django.shortcuts import get_object_or_404
from panel.models import *
from rest_framework.generics import ListAPIView, CreateAPIView
from api.serializers import PlatosSerializer, ListCategoryByUuid, PostNewOrder
from panel.models import *
from rest_framework import status
from rest_framework.response import Response
from api.helper import ApiResponse


class DishView(ListAPIView):
    http_method_names = ['get'] 
    serializer_class = PlatosSerializer
    model = Dish
    lookup_field = 'brand_uuid'

    def get_queryset(self):
        brand_uuid = self.kwargs.get('brand_uuid')
        category_uuid = self.kwargs.get('category_uuid')
        brand = get_object_or_404(Brand, uuid=brand_uuid)
        category = get_object_or_404(Category, uuid=category_uuid)

        return Dish.objects.filter(brand=brand, category=category)


class CategoryView(ListAPIView):
    http_method_names = ['get'] 
    serializer_class = ListCategoryByUuid
    model = Category
    lookup_field = 'brand_uuid'

    def get_queryset(self):
        brand_uuid = self.kwargs.get('brand_uuid')
        brand = get_object_or_404(Brand, uuid=brand_uuid)

        categories = []
        for category in Category.objects.filter(brand=brand):
            categories.append({
                "key": category.uuid,
                "icon": "x",
                "label": category.name 
            })

        return categories


class OrderView(CreateAPIView):
    serializer_class = PostNewOrder

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        if serializer.is_valid():
            all_dishes = [dish["dish_uuid"] for dish in request.data]
            dishes = [get_object_or_404(Dish, uuid=dish) for dish in all_dishes]
            new_order = Order(order_placed_at=datetime.now(), order_delivered_at=datetime.now(), ws_code="RANDOMSTRINGFORWS")
            new_order.save()

            for dish in dishes:
                new_order.dishes.add(dish)
            new_order.save()

            headers = self.get_success_headers(serializer.data)
            rsp = ApiResponse(data={"msg": f'Order placed! Your tracking number is {new_order.ws_code}'},
                              status=status.HTTP_201_CREATED, 
                              headers=headers)
            return rsp.response()
