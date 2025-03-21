from django.db import models

class Meetings(models.Model):
    id = models.AutoField(primary_key=True)
    duration = models.IntegerField(null=True, blank=True)
    speaker_count = models.IntegerField(null=True, blank=True)
    is_alive = models.BooleanField(default=True)
    segment_count = models.IntegerField(default=0, null=True, blank=True)


class Speakers(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, unique=True, null=True, blank=True)
    # most_matching_recorded_speaker = models.ForeignKey(EmbeddedSpeakers, on_delete=models.CASCADE, null=True,
    #                                                    blank=True)
    # score = models.FloatField(null=True, blank=True)


class Segments(models.Model):
    id = models.AutoField(primary_key=True)
    text = models.TextField(null=True, blank=True)
    path = models.FileField(null=True, blank=True)
    speaker = models.ForeignKey(Speakers, related_name='segments', on_delete=models.CASCADE, null=True, blank=True)
    Meating = models.ForeignKey(Meetings, related_name='segments', on_delete=models.CASCADE, null=True, blank=True)

