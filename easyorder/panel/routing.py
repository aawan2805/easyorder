# chat/routing.py

from django.urls import path

from panel.consumers import OrderConsumer

websocket_urlpatterns = [
    path('orders/brand/<uuid:brand_uuid>', OrderConsumer.as_asgi()),
]
