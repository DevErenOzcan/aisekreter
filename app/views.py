import os
from time import sleep
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from app.models import Meetings
import re


def home(request):
    return render(request, 'home.html')

@csrf_exempt
def start_meeting(request):
    if request.method == "POST":
        try:
            meeting = Meetings.objects.create()
            return JsonResponse({'success': True, 'id': meeting.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return JsonResponse({'success': False, 'error': "method not allowed"})


@csrf_exempt
def start_processes(request, id):
    if request.method == "POST":
        try:
            sleep(10)
            while Meetings.objects.get(id=id).is_alive:
                sleep(10)
                directory = f"meetings/{id}/"
                files = os.listdir(directory)

                for file in files:
                    file_path = os.path.join(directory, file)
                    meeting = Meetings.objects.get(id=id)
                    file_number = int(re.search(r'/(\d+)\.wav$', file_path).group(1))
                    if os.path.isfile(file_path) and file_number > meeting.segment_count:
                        meeting.segment_count += 1
                        meeting.save()
                        with open(file_path, 'r', encoding='utf-8') as f:
                            audio_bytes = f.read()
                        # TODO: Segment için yapılacak tüm işlemler

                return JsonResponse({'success': True, 'message': "İşlemler bitti"})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return JsonResponse({'success': False, 'error': "method not allowed"})

@csrf_exempt
def stop_meeting(request, id):
    if request.method == "POST":
        meeting_object = Meetings.objects.get(id=id)
        meeting_object.is_alive = False
        meeting_object.save()
        return JsonResponse({'success': True, 'message': "toplantı bitti"})

def get_results(request, id):
    if request.method == "POST":
        # Fetch transcription results for the given meeting ID (`id`)
        return JsonResponse({'status': 'success', 'speaker_segments': []})


