from django.shortcuts import get_object_or_404
from panel.models import *
from rest_framework.generics import ListAPIView
from api.serializers import PlatosSerializer
from panel.models import *


class DishView(ListAPIView):
    http_method_names = ['get'] 
    serializer_class = PlatosSerializer
    model = Dish
    lookup_field = 'brand_uuid'

    def get_queryset(self):
        brand_uuid = self.kwargs.get('brand_uuid')
        brand = get_object_or_404(Brand, uuid=brand_uuid)
        return Dish.objects.filter(brand=brand)
