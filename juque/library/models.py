from django.db import models
from django.utils import timezone
from django.conf import settings
from juque.core.models import User
import csv
import os

class Artist (models.Model):
    name = models.CharField(max_length=200, unique=True)
    match_name = models.CharField(max_length=200, db_index=True)

    def __unicode__(self):
        return self.name

class Album (models.Model):
    name = models.CharField(max_length=200)
    artist = models.ForeignKey(Artist, related_name='albums', null=True, blank=True)
    match_name = models.CharField(max_length=200, db_index=True)

    def __unicode__(self):
        return self.name

class Genre (models.Model):
    name = models.CharField(max_length=200, unique=True)
    match_name = models.CharField(max_length=200, db_index=True)

    def __unicode__(self):
        return self.name

class Track (models.Model):
    owner = models.ForeignKey(User, related_name='tracks')
    name = models.CharField(max_length=200)
    length = models.FloatField()
    bitrate = models.IntegerField()
    sample_rate = models.IntegerField()
    artist = models.ForeignKey(Artist, related_name='tracks', null=True, blank=True)
    album = models.ForeignKey(Album, related_name='tracks', null=True, blank=True)
    genre = models.ForeignKey(Genre, related_name='tracks', null=True, blank=True)
    track_number = models.IntegerField(default=0)
    file_path = models.TextField(blank=True)
    # The key and IV used to encrypt the segment files.
    aes_key = models.CharField(max_length=32)
    aes_iv = models.CharField(max_length=32)
    date_added = models.DateTimeField(default=timezone.now, editable=False)

    def __unicode__(self):
        return self.name

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
