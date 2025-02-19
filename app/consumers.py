import os
import io
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
import aiofiles
import wave
import numpy as np


class AudioConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.meeting_id = None
        self.segment_count = 0
        self.header = None
        self.data = bytearray()

    async def connect(self):
        self.meeting_id = self.scope['url_route']['kwargs']['meeting_id']
        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data:
            if self.header is None:
                self.header = bytes_data[:44]
                print("header received")
                self.data = bytes_data[44:]

            else:
                self.data += bytes_data
            print("-" * 100)
            print(f"Received {len(bytes_data)} bytes")
            await self.process_audio()

    async def process_audio(self):
        audio_data = self.header + bytes(self.data)
        audio_file = io.BytesIO(audio_data)
        diarization_result = settings.DIARIZATION_MODEL(
            {'audio': audio_file, 'uri': f"meeting_{self.meeting_id}{self.segment_count}"})

        segments = list(diarization_result.itertracks(yield_label=True))
        for i, (segment, seg_char, speaker) in enumerate(segments):
            # sample rate 48.000 her sample başına düşen byte sayısı 2
            start_byte = int(segment.start * 48000 * 2)
            end_byte = int(segment.end * 48000 * 2)
            segment_data = self.data[start_byte:end_byte]
            print(f"{i}.segment size: {len(segment_data)} bytes")

            # segment 0.3 saniyeden büyükse ve son segment değilse işleme sokuyorum
            if len(segment_data) > 30000 and i != len(segments) - 1:
                await self.save_audio(f"meetings/{self.meeting_id}/{self.segment_count}.wav", self.header + segment_data)
                self.data = self.data[end_byte:]
                self.segment_count += 1
                print(f"meetings/{self.meeting_id}/{self.segment_count}.wav saved")

    async def save_audio(self, filename, data):
        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        async with aiofiles.open(filename, 'ab') as temp_file:
            await temp_file.write(data)

    async def disconnect(self, close_code):
        print("Connection closed.")
