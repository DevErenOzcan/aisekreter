import asyncio
import aiofiles
import aiofiles.os
import os
from channels.generic.websocket import AsyncWebsocketConsumer
from pydub import AudioSegment
from django.conf import settings
from sqlalchemy import Nullable


class AudioConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.meeting_id = None
        self.buffer = bytearray()  # Bellekte ses verisini tutan buffer
        self.chunk_count = 0
        self.header = None

    async def connect(self):
        self.meeting_id = self.scope['url_route']['kwargs']['meeting_id']
        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data:
            self.buffer.extend(bytes_data)
            print(bytes_data)
            # print(f"Received {len(bytes_data)} bytes, buffer size: {len(self.buffer)}")
            #
            # webm_filename = f"meetings/{self.meeting_id}/{self.chunk_count}.webm"
            wav_filename = f"meetings/{self.meeting_id}/{self.chunk_count}.wav"

            await self.save_audio(wav_filename, bytes_data)
            self.chunk_count += 1

            # await self.convert_to_wav(webm_filename, wav_filename)

            # await aiofiles.os.remove(webm_filename)

            # print(f"{wav_filename} saved.")

    async def save_audio(self, filename, data):
        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        async with aiofiles.open(filename, 'ab') as temp_file:
            await temp_file.write(data)

    async def convert_to_wav(self, input_file, output_file):
        # Pydub ile audio dosyasını WAV formatına dönüştürme
        try:
            audio = AudioSegment.from_file(input_file, format="webm")
            audio = audio.set_frame_rate(48000).set_channels(1)
            audio.export(output_file, format="wav")
        except Exception as e:
            print(f"Error converting {input_file} to WAV: {e}")

    async def disconnect(self, close_code):
        print("Connection closed.")
