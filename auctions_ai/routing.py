# routing.py
from django.urls import path

from auctions_ai.consumers import ChatConsumer

websocket_urlpatterns = [
    path("ws/chat/", ChatConsumer.as_asgi()),
]
