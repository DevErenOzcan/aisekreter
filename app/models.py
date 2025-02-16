from django.db import models

class Meeting(models.Model):
    id = models.AutoField(primary_key=True)
    duration = models.IntegerField(null=True, blank=True)
    speaker_count = models.IntegerField(null=True, blank=True)
    is_alive = models.BooleanField(default=True)


class Speaker(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, unique=True, null=True, blank=True)
    # most_matching_recorded_speaker = models.ForeignKey(EmbeddedSpeakers, on_delete=models.CASCADE, null=True,
    #                                                    blank=True)
    # score = models.FloatField(null=True, blank=True)


class Segment(models.Model):
    id = models.AutoField(primary_key=True)
    start = models.FloatField(null=True, blank=True)
    end = models.FloatField(null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    audio = models.FileField(null=True, blank=True)
    speaker = models.ForeignKey(Speaker, related_name='segments', on_delete=models.CASCADE, null=True, blank=True)
    Meating = models.ForeignKey(Meeting, related_name='segments', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Segment ({self.start}-{self.end}): {self.text[:30]}..."


class Word(models.Model):
    id = models.AutoField(primary_key=True)
    segment = models.ForeignKey(Segment, related_name='words', on_delete=models.CASCADE)
    speaker = models.ForeignKey(Speaker, related_name='words', on_delete=models.CASCADE, null=True, blank=True)
    word = models.CharField(max_length=50, null=True, blank=True)
    start = models.FloatField(null=True, blank=True)
    end = models.FloatField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Word: {self.word} ({self.start}-{self.end})"


# class VoiceSentiment(models.Model):
#     id = models.AutoField(primary_key=True)
#     Happy = models.FloatField(null=True, blank=True)
#     Angry = models.FloatField(null=True, blank=True)
#     Sad = models.FloatField(null=True, blank=True)
#     segment = models.ForeignKey(Segment, related_name='sentiments', on_delete=models.CASCADE)
#
#
# class TextSentiment(models.Model):
#     id = models.AutoField(primary_key=True)
#     Happy = models.FloatField(null=True, blank=True)
#     Angry = models.FloatField(null=True, blank=True)
#     Sad = models.FloatField(null=True, blank=True)
#     segment = models.ForeignKey(Segment, related_name='sentiments', on_delete=models.CASCADE)
