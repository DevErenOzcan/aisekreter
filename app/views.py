import os
from time import sleep
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from app.models import Meeting
from pydub import AudioSegment
from pydub.utils import make_chunks
from io import BytesIO
import base64


audio_segments = {}
def home(request):
    return render(request, 'home.html')

@csrf_exempt
def start_meeting(request):
    if request.method == "POST":
        try:
            meeting = Meeting.objects.create()
            return JsonResponse({'success': True, 'id': meeting.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return JsonResponse({'success': False, 'error': "method not allowed"})


@csrf_exempt
def upload(request, id):
    if request.method == "POST":
        try:
            meeting = Meeting.objects.get(id=id)
            if meeting.is_alive:
                base64_audio_data = request.body
                audio_binary = base64.b64decode(base64_audio_data)

                directory = f"meetings/meeting_{id}"
                os.makedirs(directory, exist_ok=True)
                with open(f"{directory}/chunk_{meeting.chunk_count}.wav", "wb") as f:
                    f.write(audio_binary)
                meeting.chunk_count += 1
                meeting.save()

                return JsonResponse({'success': True, 'message': "Ses kaydedildi ve segment eklendi"})
            else:
                return JsonResponse({'success': False, 'message': "Toplantı kapalı, ses işlenmedi"})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return JsonResponse({'success': False, 'error': "method not allowed"})

@csrf_exempt
def stop_meeting(request, id):
    if request.method == "POST":
        meeting_object = Meeting.objects.get(id=id)
        meeting_object.is_alive = False
        meeting_object.save()
        return JsonResponse({'success': True, 'message': "toplantı bitti"})

def get_results(request, id):
    if request.method == "POST":
        # Fetch transcription results for the given meeting ID (`id`)
        return JsonResponse({'status': 'success', 'speaker_segments': []})


