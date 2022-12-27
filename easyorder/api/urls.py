from django.urls import path
from api.views import DishView


urlpatterns = [
    path('dishes/<uuid:brand_uuid>', DishView.as_view(), name='get-platos'),
]
