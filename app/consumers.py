import os
import io
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
import aiofiles
from pydub import AudioSegment
import torchaudio


class AudioConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.meeting_id = None
        self.segment_count = 0
        self.last_segment_end = None
        self.audio_segment = AudioSegment.silent(duration=0)


    async def connect(self):
        self.meeting_id = self.scope['url_route']['kwargs']['meeting_id']
        await self.accept()


    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data:
            audio_stream = io.BytesIO(bytes_data)
            new_segment = AudioSegment.from_file(audio_stream, format="wav")
            self.audio_segment += new_segment

            print("-" * 100)
            print(f"Received {len(bytes_data)} bytes and added to AudioSegment")
            await self.process_audio()


    async def process_audio(self):
        audio_buffer = io.BytesIO()
        self.audio_segment.export(audio_buffer, format="wav")
        audio_buffer.seek(0)
        waveform, sample_rate = torchaudio.load(audio_buffer)

        diarization_result = settings.DIARIZATION_MODEL(
            {"uri": "memory_audio", "waveform": waveform, "sample_rate": sample_rate})

        segments = list(diarization_result.itertracks(yield_label=True))
        for i, (segment, seg_char, speaker) in enumerate(segments):
            # segment datasını ms cinsinden alıyorum o yüzden 1000
            start_time = int(segment.start * 1000)
            end_time = int(segment.end * 1000)
            segment_data = self.audio_segment[start_time:end_time]
            print(f"{i}.segment size: {len(segment_data)} ms")

            # segment 0.3 saniyeden büyükse ve son segment değilse işleme sokuyorum
            if len(segment_data) > 300 and i != len(segments) - 1:
                await self.save_audio(f"meetings/{self.meeting_id}/{self.segment_count}.wav", segment_data)
                self.audio_segment = self.audio_segment[end_time:]
                self.segment_count += 1
                print(f"meetings/{self.meeting_id}/{self.segment_count}.wav saved")


    async def save_audio(self, filename, data):
        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        data.export(filename, format="wav")


    async def disconnect(self, close_code):
        print("Connection closed.")
