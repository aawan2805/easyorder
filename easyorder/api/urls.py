from django.urls import path
from api.views import DishView


urlpatterns = [
    path('dishes', DishView.as_view(), name='get-platos'),
]
