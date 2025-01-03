from django.urls import path
from .consumers import NotificationConsumer
websocket_patterns = [
    path("ws/notifications/", NotificationConsumer.as_asgi()),
]
