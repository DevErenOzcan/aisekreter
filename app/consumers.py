import wave
from channels.generic.websocket import AsyncWebsocketConsumer

class AudioConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.audio_data = b""  # Gelen veriyi saklamak için buffer
        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data:
            self.audio_data += bytes_data  # Gelen veriyi biriktir

    async def disconnect(self, close_code):
        # Bağlantı kapandığında dosyaya kaydet
        if self.audio_data:
            self.save_audio(self.audio_data, "recorded_audio.wav")

    def save_audio(self, binary_data, filename):
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(binary_data)
