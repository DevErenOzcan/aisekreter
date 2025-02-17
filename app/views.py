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
def start_segmentation(request, id):
    if request.method == "POST":
        try:
            sleep(2)
            while Meeting.objects.get(id=id).is_alive:
                sleep(3)
                with open(f"meetings/{id}", 'rb') as f:
                    audio_file = f.read()
                return JsonResponse({'success': True, 'message': "Segmentasyon bitti"})

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


