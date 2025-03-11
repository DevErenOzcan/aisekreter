import os
import io
import wave

import webrtcvad
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
import aiofiles
from pydub import AudioSegment
import torchaudio

# VAD nesnesini oluşturup modunu ayarlıyorum
vad = webrtcvad.Vad()
vad.set_mode(1)  # 0 ile 3 arasında bir değer

sr = 48000
frame_duration = 20  # ms
frame_size = int(sr * frame_duration / 1000)


class AudioConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.meeting_id = None
        self.segment_count = 0
        self.buffer = bytearray()
        self.segments = []
        self.current_segment = bytearray()
        self.not_speech_buffer = bytearray()
        self.is_speech_now = False

    async def connect(self):
        self.meeting_id = self.scope['url_route']['kwargs']['meeting_id']
        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data:
            # bytes data da 44 byte lık header var. Bu header ı atıyorum
            bytes_data = bytes_data[44:]

            bytes_data = self.buffer + bytes_data
            samples = bytes_data[:len(bytes_data) // 960 * 960]
            self.buffer = bytes_data[len(samples):]
            for i in range(0, len(samples), frame_size):
                frame_data = samples[i:i + frame_size]
                is_speech = vad.is_speech(frame_data, sr)

                if is_speech:
                    if self.is_speech_now:
                        self.current_segment += frame_data

                    else:
                        # segment 2 sn den kısaysa sessizlik bufferına ekliyorum
                        if len(self.current_segment) < sr * 2:
                            self.current_segment += frame_data

                        else:
                            # mevcut segmentin sonuna "not_speech_buffer" daki sessizlğin yarısını ekleyip segmenti kaydediyorum
                            self.current_segment += self.not_speech_buffer[int(len(self.not_speech_buffer) / 2):]
                            self.segments.append(self.current_segment)

                            file_path = f"segments/segment_{self.segment_count}.wav"
                            await self.save_audio(file_path, self.current_segment)
                            self.segment_count += 1

                            print("-" * 100)
                            print(f"new segment saved: {len(self.current_segment)/96000} sn")

                            # mevcut segmenti temizleyip yeni segmente kalan sessizliği ekliyorum. Böylece ses parçaları arasında kesinti olmuyor
                            self.current_segment = bytearray()
                            self.current_segment += self.not_speech_buffer[:int(len(self.not_speech_buffer) / 2)]
                            self.not_speech_buffer = bytearray()

                            # son olarak yeni segmente "frame_data" yı ekliyorum
                            self.current_segment += frame_data

                else:
                    if self.is_speech_now:
                        self.not_speech_buffer += frame_data

                    else:
                        self.not_speech_buffer += frame_data

                self.is_speech_now = is_speech

    async def save_audio(self, filename, data):
        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        with wave.open(filename, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(48000)
            wav_file.writeframes(data)

    async def disconnect(self, close_code):
        print("Connection closed.")
