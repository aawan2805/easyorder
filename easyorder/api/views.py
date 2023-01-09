from django.shortcuts import get_object_or_404
from panel.models import *
from rest_framework.generics import ListAPIView
from api.serializers import PlatosSerializer, ListCategoryByUuid
from panel.models import *


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
