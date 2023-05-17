# chat/routing.py

from django.urls import path

from panel.consumers import OrderConsumer, CollectionCodeConsumer

websocket_urlpatterns = [
    path('orders/brand/<uuid:brand_uuid>', OrderConsumer.as_asgi()),
    path('orders/client/<str:collection_code>', CollectionCodeConsumer.as_asgi()),
]
