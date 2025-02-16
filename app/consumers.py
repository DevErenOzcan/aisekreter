from urllib.parse import parse_qs
from channels.generic.websocket import AsyncWebsocketConsumer
from pydub import AudioSegment
import io

# Toplantı ID'lerine göre sesi saklamak için global değişken
meeting_audio_buffers = {}

class AudioStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        query_params = parse_qs(self.scope["query_string"].decode())
        self.meeting_id = query_params.get("meeting_id", [None])[0]  # Meeting ID al

        if not self.meeting_id:
            await self.close()  # Meeting ID yoksa bağlantıyı kapat

        # Eğer meeting_id için bir buffer yoksa oluştur
        if self.meeting_id not in meeting_audio_buffers:
            meeting_audio_buffers[self.meeting_id] = AudioSegment.silent(duration=0)

        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data:
            await self.process_audio_chunk(bytes_data)

    async def process_audio_chunk(self, audio_chunk):
        """
        Gelen sesi global değişkende sakla.
        """
        # Bytes verisini Pydub'un AudioSegment nesnesine çevir
        try:
            audio_segment = AudioSegment.from_raw(
                io.BytesIO(audio_chunk),
                sample_width=2,  # 16-bit PCM için 2 byte
                frame_rate=16000,  # Kullanıcıdan gelen sesin örnekleme hızı
                channels=1  # Mono ses
            )
            # Gelen sesi global buffer'a ekle
            meeting_audio_buffers[self.meeting_id] += audio_segment
        except Exception as e:
            print(f"Audio processing error: {e}")

    async def disconnect(self, close_code):
        await self.close()


def get_audio_buffers(meeting_id):
    """View içinden bu fonksiyon ile ses verisini alabiliriz."""
    return meeting_audio_buffers.get(meeting_id, None)