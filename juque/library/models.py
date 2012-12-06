from django.db import models
from django.utils import timezone
from django.conf import settings
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
    name = models.CharField(max_length=200)
    length = models.FloatField()
    bitrate = models.IntegerField()
    sample_rate = models.IntegerField()
    artist = models.ForeignKey(Artist, related_name='songs', null=True, blank=True)
    album = models.ForeignKey(Album, related_name='songs', null=True, blank=True)
    genre = models.ForeignKey(Genre, related_name='songs', null=True, blank=True)
    track_number = models.IntegerField(default=0)
    # The key and IV used to encrypt the segment files.
    aes_key = models.CharField(max_length=32)
    aes_iv = models.CharField(max_length=32)
    date_added = models.DateTimeField(default=timezone.now, editable=False)

    def __unicode__(self):
        return self.name

    def get_root(self):
        return os.path.join(settings.MEDIA_ROOT, 'tracks', str(self.pk))
    media_root = property(get_root)

    def segments(self):
        seg_file = os.path.join(self.media_root, 'segments.csv')
        with open(seg_file, 'rb') as f:
            for row in csv.reader(f):
                url = '%stracks/%s/%s' % (settings.MEDIA_URL, self.pk, row[0])
                length = float(row[2]) - float(row[1])
                yield url, length
