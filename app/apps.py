import joblib
from django.apps import AppConfig
from django.conf import settings
from pyannote.audio import Model, Inference


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        settings.DIARIZATION = Inference("pyannote/speaker-diarization", device="cuda")
