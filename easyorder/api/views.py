from panel.models import *
from rest_framework.generics import ListAPIView
from api.serializers import PlatosSerializer
from panel.models import *

class DishView(ListAPIView):
    http_method_names = ['get'] 
    serializer_class = PlatosSerializer
    model = Dish

    def get_queryset(self):
        return Dish.objects.all()
