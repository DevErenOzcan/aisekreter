from django.apps import AppConfig
from django.conf import settings
from joblib import load
from tensorflow.keras.models import load_model


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        settings.SCALER = load('app/models/scaler.pkl')
        settings.BEST_KERAS = load_model('app/models/best_model.keras')
        settings.LABEL_ENCODER = load('app/models/label_encoder.pkl')
