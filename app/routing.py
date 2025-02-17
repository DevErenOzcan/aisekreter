from django.urls import re_path
from .consumers import AudioConsumer

websocket_urlpatterns = [
    re_path(r'ws/audio-stream/$', AudioConsumer.as_asgi()),
]
