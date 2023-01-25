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


    def get(self, request, *args, **kwargs):
        response = super().get(self, request, *args, **kwargs)
        response['Access-Control-Allow-Credentials'] = 'true'
        return response


class CategoryView(ListAPIView):
    http_method_names = ['get'] 
    serializer_class = ListCategoryByUuid
    model = Category
    lookup_field = 'brand_uuid'
    brand = None

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

    def get(self, request, *args, **kwargs):
        response = super().get(self, request, *args, **kwargs)
        if 'brand' not in request.COOKIES:
            # Setting the cookie for 30 mins to store the brand uuid
            response.set_cookie('brand', self.brand or self.kwargs.get('brand_uuid'), max_age=30)
        else:
            print(request.COOKIES['brand'])

        response['Access-Control-Allow-Credentials'] = 'true'
        return response


class OrderView(CreateAPIView):
    serializer_class = PostNewOrder

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        if serializer.is_valid():
            total_amount = 0.0
            all_dishes = [dish["dish_uuid"] for dish in request.data]
            dishes = []
            for dish in all_dishes:
                aux = get_object_or_404(Dish, uuid=dish)
                dishes.append(aux)
                total_amount += aux.price

            new_order = Order(order_placed_at=datetime.now(),
                              order_delivered_at=datetime.now(), 
                              ws_code="RANDOMSTRINGFORWS",
                              brand=Brand.objects.get(uuid="e46ba39f-6227-48d4-9380-f941727a643f"),
                              amount=total_amount)
            new_order.save()

            for dish in dishes:
                new_order.dishes.add(dish)
            new_order.save()

            headers = self.get_success_headers(serializer.data)
            rsp = ApiResponse(data={"msg": f'Order placed! Your tracking number is {new_order.ws_code}'},
                              status=status.HTTP_201_CREATED, 
                              headers=headers)
            return rsp.response()
