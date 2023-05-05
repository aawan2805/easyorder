from django.urls import path
from api.views import DishView, CategoryView, OrderView, OrderStatus, QRStatus, SummaryOrderStatus


urlpatterns = [
    path('dishes/<uuid:brand_uuid>/<uuid:category_uuid>', DishView.as_view(), name='get-platos'),
    path('category/<uuid:brand_uuid>', CategoryView.as_view(), name='get-category'),
    path('order', OrderView.as_view(), name='make-new-order'),
    path('check-order-status/<str:collection_code>', OrderStatus.as_view()),
    path('check-qr/<uuid:brand_uuid>', QRStatus.as_view()),
    path('summary-order-status/<str:collection_code>', SummaryOrderStatus.as_view())
]
