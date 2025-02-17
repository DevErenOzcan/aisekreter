from django.urls import re_path
from app.consumers import AudioConsumer

websocket_urlpatterns = [
    re_path(r'meeting/(?P<meeting_id>\d+)/$', AudioConsumer.as_asgi()),
]
