import aiofiles
from channels.generic.websocket import AsyncWebsocketConsumer
from pydub import AudioSegment

class AudioConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.meeting_id = self.scope['url_route']['kwargs']['meeting_id']
        self.filename = f"meetings/{self.meeting_id}.wav"  # Geçici WebM dosyası
        self.file = await aiofiles.open(self.filename, 'wb')  # Asenkron dosya açma
        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data:
            print("byte data received")
            await self.file.write(bytes_data)  # Gelen veriyi sırayla dosyaya yaz

    async def disconnect(self, close_code):
        await self.file.close()

