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
vad.set_mode(2)  # 0 ile 3 arasında bir değer

sr = 48000
frame_duration = 20  # ms
frame_size = int(sr * frame_duration / 1000)


class AudioConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.meeting_id = None
        self.segment_count = 0
        self.buffer = bytearray()
        self.current_segment = bytearray()
        self.is_speech_now = False
        self.not_speech_count = 0

    async def connect(self):
        self.meeting_id = self.scope['url_route']['kwargs']['meeting_id']
        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data:
            # bytes data da 44 byte lık header var. Bu header ı atıyorum
            bytes_data = bytes_data[44:]

            # buffer da kalan data yı ekliyorum
            bytes_data = self.buffer + bytes_data

            # bytes data nın 960 a tam bölünen kısmını alıyorum. Kalan kısmı bir sonraki datada kullanmak için buffer a ekliyorum
            useable_data_len = int(len(bytes_data) // frame_size * frame_size)
            samples = bytes_data[:useable_data_len]
            self.buffer = bytes_data[useable_data_len:]

            for i in range(0, len(samples), frame_size):
                frame_data = samples[i:i + frame_size]
                is_speech = vad.is_speech(frame_data, sr)

                if is_speech:
                    if not self.is_speech_now:
                        # sessizlik 24 frame den fazlaysa ve segment 3 sn den uzunsa mevcut segmenti bölüyorum
                        if len(self.current_segment) > sr * 6:
                            if self.not_speech_count > 10:
                                # son segmentin son kısmındaki sessizliğin ilk yarısını o segmentte bırakıp diğer yarısını yeni segmente ekleyeceğim
                                # böylelikle sesi tam olarak sessizliğin ortasından bölmüş oluyorum.
                                not_speech_len = self.not_speech_count * frame_size
                                not_speech_buffer = self.current_segment[-int(not_speech_len / 2):]
                                self.current_segment = self.current_segment[:-int(not_speech_len / 2)]

                                file_path = f"meetings/meet_{self.meeting_id}/segment_{self.segment_count}.wav"
                                await self.save_audio(file_path, self.current_segment)
                                self.segment_count += 1

                                print("-" * 100)
                                print(f"new segment saved: {len(self.current_segment) / (sr * 2)} sn")

                                # mevcut segmenti temizleyip yeni segmentin başına kalan yarısını ekliyorum. Böylece ses parçaları arasında kesinti olmuyor
                                self.current_segment = bytearray()
                                self.current_segment = not_speech_buffer

                        self.not_speech_count = 0

                else:
                    self.not_speech_count += 1

                self.is_speech_now = is_speech
                self.current_segment += frame_data


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
        file_path = f"meetings/meet_{self.meeting_id}/segment_{self.segment_count}.wav"
        await self.save_audio(file_path, self.current_segment)

        print("-" * 100)
        print(f"new segment saved: {len(self.current_segment) / (sr * 2)} sn")
        print("Connection closed.")
