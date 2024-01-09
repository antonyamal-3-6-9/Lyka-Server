from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from . import consumer
from django.core.asgi import get_asgi_application


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            [
                path("ws/notification/private/<int:user_id>/", consumer.NotificationPrivateConsumer.as_asgi()),
            ]
        )
    ),
})