from django.urls import path
from . import consumers

websocket_patterns = [
    path('chat/chatwindow/appointmentcall/<str:room_name>/', consumers.ChatConsumer.as_asgi())
]