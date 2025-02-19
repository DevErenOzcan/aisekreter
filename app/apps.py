import joblib
from django.apps import AppConfig
from django.conf import settings
from pyannote.audio import Model, Inference, Pipeline


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        settings.DIARIZATION = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token="<hf_token>")
