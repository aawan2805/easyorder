"""
ASGI config for easyorder project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

import panel.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'easyorder.settings')

application = ProtocolTypeRouter({
  'http': get_asgi_application(),
    'websocket': URLRouter(
      panel.routing.websocket_urlpatterns
    ),
})