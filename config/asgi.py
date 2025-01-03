import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from app.chat.routing import websocket_patterns as chat_websocket_patterns
from app.notification.routing import websocket_patterns as notifications_websocket_patterns

# Set the default Django settings module for the 'asgi' application.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

"""
ASGI configuration for the project.

This configuration file sets up the ASGI application to handle HTTP requests 
and WebSocket connections. It uses Django Channels to route WebSocket 
connections to the appropriate application based on the URL patterns.

The ProtocolTypeRouter is used to route requests based on their type:
- HTTP requests are handled by Django's ASGI application.
- WebSocket requests are handled by Channels with an authentication middleware stack.

WebSocket routing combines patterns from both the chat and notifications apps.
"""

application = ProtocolTypeRouter({
    # Routes HTTP requests to Django's ASGI application
    "http": get_asgi_application(),  
    # Routes WebSocket requests to the appropriate application
    'websocket': AuthMiddlewareStack(
        URLRouter(
            # Combines WebSocket URL patterns from chat and notifications apps
            chat_websocket_patterns + notifications_websocket_patterns
        )
    )
})




# # """
# # ASGI config for config project.

# # It exposes the ASGI callable as a module-level variable named ``application``.

# # For more information on this file, see
# # https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
# # """

# # import os

# # from django.core.asgi import get_asgi_application

# # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# # application = get_asgi_application()
# """
# ASGI config for odas project.

# It exposes the ASGI callable as a module-level variable named ``application``.

# For more information on this file, see
# https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
# """


# import os

# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# from django.core.asgi import get_asgi_application
# from app.chat.routing import websocket_patterns

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# application = ProtocolTypeRouter({
#     "http": get_asgi_application(), 
#     # Just HTTP for now. (We can add other protocols later.)
#     'websocket' : AuthMiddlewareStack(
#         URLRouter(
#             websocket_patterns
#         )
#     )
# })