import os
import io
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings

import librosa
import numpy as np
import pandas as pd
import wave
import webrtcvad

from app.whisperx.audio import load_audio



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
        self.segment_id = None
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
                                self.segment_id = self.segment_count
                                self.segment_count += 1

                                print("-" * 100)
                                print(f"new segment saved: {len(self.current_segment) / (sr * 2)} sn")

                                await self.process_audio(self.current_segment)

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


    async def process_audio(self, data):
        # Bellekte bir WAV dosyası oluştur
        wav_buffer = io.BytesIO()

        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit PCM (2 byte per sample)
            wav_file.setframerate(16000)  # 16 kHz örnekleme oranı
            wav_file.writeframes(data)  # Ham sesi yaz

        wav_buffer.seek(0)

        await transcription(f"meetings/meet_{self.meeting_id}/segment_{self.segment_id}.wav")

        features = extract_features(wav_buffer)

        if isinstance(features, Exception):
            print("Feature extraction error:", features)
            return

        columns = (
                ['zero_crossing', 'centroid_mean', 'rolloff_mean', 'bandwidth_mean'] +
                [f'contrast_mean_{i}' for i in range(7)] +
                [f'contrast_std_{i}' for i in range(7)] +
                [f'chroma_stft_mean_{i}' for i in range(12)] +
                [f'chroma_stft_std_{i}' for i in range(12)] +
                ['rms_mean', 'melspectrogram_mean', 'melspectrogram_std', 'flatness_mean'] +
                [f'poly_mean_{i}' for i in range(2)] +
                [f'mfcc_mean_{i}' for i in range(40)] +
                [f'mfcc_std_{i}' for i in range(40)] +
                ['energy']
        )

        df = pd.DataFrame([features], columns=columns)


        # Özellikleri ayır
        new_features = df.values

        # Scaler'ı yükle
        scaler = settings.SCALER

        # Veriyi scaler ile ölçeklendir
        new_features_scaled = scaler.transform(new_features)

        # CNN modeline uygun shaping işlemi
        new_features_scaled = new_features_scaled.reshape(new_features_scaled.shape[0], new_features_scaled.shape[1], 1)

        # Eğitilmiş en iyi modeli yükle
        best_model = settings.BEST_KERAS

        # Tahminleri elde et
        predictions = best_model.predict(new_features_scaled)

        # Tahminleri orijinal etikete dönüştürmek için LabelEncoder'ı yükle
        label_encoder = settings.LABEL_ENCODER

        # Tahmin edilen sınıfları al
        predicted_classes = np.argmax(predictions, axis=1)
        predicted_labels = label_encoder.inverse_transform(predicted_classes)

        # Sonuçları yazdır
        print(predicted_labels)


def extract_features(wav_file):
    try:
        audio, sample_rate = librosa.load(wav_file, sr=sr)

        zero_crossing = np.mean(librosa.feature.zero_crossing_rate(y=audio).T, axis=0)
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=audio, sr=sample_rate).T, axis=0)
        spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=audio, sr=sample_rate).T, axis=0)
        spectral_bandwidth = np.mean(librosa.feature.spectral_bandwidth(y=audio, sr=sample_rate).T, axis=0)
        spectral_contrast = librosa.feature.spectral_contrast(y=audio, sr=sample_rate)
        contrast_mean = np.mean(spectral_contrast, axis=1)
        contrast_std = np.std(spectral_contrast, axis=1)

        chroma_stft = librosa.feature.chroma_stft(y=audio, sr=sample_rate)
        chroma_stft_mean = np.mean(chroma_stft, axis=1)
        chroma_stft_std = np.std(chroma_stft, axis=1)

        rms_mean = np.mean(librosa.feature.rms(y=audio))

        mel_spectrogram = librosa.feature.melspectrogram(y=audio, sr=sample_rate)
        melspectrogram_mean = np.mean(mel_spectrogram)
        melspectrogram_std = np.std(mel_spectrogram)

        flatness_mean = np.mean(librosa.feature.spectral_flatness(y=audio))

        poly_features = librosa.feature.poly_features(y=audio, sr=sample_rate, order=1)
        poly_mean = np.mean(poly_features, axis=1)

        mfcc = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=40)
        mfcc_mean = np.mean(mfcc, axis=1)
        mfcc_std = np.std(mfcc, axis=1)

        energy = np.sum(audio ** 2)

        features = np.hstack([
            zero_crossing, spectral_centroid, spectral_rolloff, spectral_bandwidth,
            contrast_mean, contrast_std, chroma_stft_mean, chroma_stft_std,
            rms_mean, melspectrogram_mean, melspectrogram_std, flatness_mean,
            poly_mean, mfcc_mean, mfcc_std, energy
        ])

        return features

    except Exception as e:
        return e


async def transcription(file):
    try:
        audio = load_audio(file)
        result = settings.TRANSCRIBE_MODEL.transcribe(audio, batch_size=16)
        print(result)
        return result
    except Exception as e:
        print(e)
        return e