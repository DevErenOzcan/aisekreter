import asyncio
import aiofiles
import wave
from channels.generic.websocket import AsyncWebsocketConsumer

class AudioConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.filename = "recorded_audio.webm"  # Geçici WebM dosyası
        self.file = await aiofiles.open(self.filename, 'wb')  # Asenkron dosya açma
        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data:
            await self.file.write(bytes_data)  # Gelen veriyi sırayla dosyaya yaz

    async def disconnect(self, close_code):
        await self.file.close()  # Dosyayı kapat
