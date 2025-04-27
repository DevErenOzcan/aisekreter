import os
from django.core.asgi import get_asgi_application
from django.conf import settings
from channels.routing import ProtocolTypeRouter, URLRouter
from app.routing import websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aisekreter.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(websocket_urlpatterns),
})


# whisperx modelleri
from app.whisperx.asr import load_model
settings.TRANSCRIBE_MODEL = load_model("large", "cuda", compute_type="float16")


# oğuzhan ın modelleri
from joblib import load
import tensorflow as tf

tf.config.set_visible_devices([], 'GPU')

settings.SCALER = load('app/models/scaler.pkl')
settings.BEST_KERAS = tf.keras.models.load_model('app/models/best_model.keras')
settings.LABEL_ENCODER = load('app/models/label_encoder.pkl')
settings.SELECTOR = load('app/models/selector.pkl')