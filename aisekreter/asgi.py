import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from app.routing import websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aisekreter.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(websocket_urlpatterns),
})

from django.conf import settings
from joblib import load
from tensorflow.keras.models import load_model

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # GPU'yu devre dışı bırak

settings.SCALER = load('app/models/scaler.pkl')
settings.BEST_KERAS = load_model('app/models/best_model.keras')
settings.LABEL_ENCODER = load('app/models/label_encoder.pkl')