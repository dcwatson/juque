from django.db import models
from django.utils import timezone
from django.conf import settings
from juque.core.models import User
import os
import re

def get_match_name(name):
    return re.sub(r'[^a-zA-Z0-9]+', '_', name).lower().strip('_')

class MatchModel (models.Model):
    name = models.CharField(max_length=200)
    match_name = models.CharField(max_length=200, db_index=True, editable=False)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.name

    def save(self, **kwargs):
        self.match_name = get_match_name(self.name)
        super(MatchModel, self).save(**kwargs)

class Artist (MatchModel):
    pass

class Album (MatchModel):
    artist = models.ForeignKey(Artist, related_name='albums', null=True, blank=True)

class Genre (MatchModel):
    pass

class Track (MatchModel):
    owner = models.ForeignKey(User, related_name='tracks')
    length = models.FloatField(editable=False)
    bitrate = models.IntegerField(editable=False)
    sample_rate = models.IntegerField(editable=False)
    artist = models.ForeignKey(Artist, related_name='tracks', null=True, blank=True)
    album = models.ForeignKey(Album, related_name='tracks', null=True, blank=True)
    genre = models.ForeignKey(Genre, related_name='tracks', null=True, blank=True)
    track_number = models.IntegerField(default=0)
    # File information
    file_path = models.TextField(editable=False)
    file_size = models.IntegerField(editable=False)
    file_hash = models.CharField(max_length=32, unique=True, editable=False)
    # Segment information (optional)
    segment_aes_key = models.CharField(max_length=32, editable=False, blank=True)
    segment_aes_iv = models.CharField(max_length=32, editable=False, blank=True)
    # System information
    date_added = models.DateTimeField(default=timezone.now, editable=False)
    date_modified = models.DateTimeField(editable=False)

    def save(self, **kwargs):
        self.date_modified = timezone.now()
        super(Track, self).save(**kwargs)

class Segment (models.Model):
    track = models.ForeignKey(Track, related_name='segments')
    start_time = models.FloatField()
    end_time = models.FloatField()
    file_path = models.TextField()

    class Meta:
        ordering = ('start_time',)

    length = property(lambda self: self.end_time - self.start_time)

    def __unicode__(self):
        return self.file_path

    def url(self):
        storage = self.track.owner.get_storage()
        return storage.url(self.file_path)
