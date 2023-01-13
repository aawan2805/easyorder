from django.urls import path
from api.views import DishView, CategoryView, OrderView


urlpatterns = [
    path('dishes/<uuid:brand_uuid>/<uuid:category_uuid>', DishView.as_view(), name='get-platos'),
    path('category/<uuid:brand_uuid>', CategoryView.as_view(), name='get-category'),
    path('order', OrderView.as_view(), name='make-new-order'),
]
