from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.urlresolvers import reverse
from juque.core.models import User
from juque.library.utils import slugify, library_storage, artwork_storage
import os
import re

FILE_TYPE_CHOICES = (
    ('audio/mp3', 'MP3'),
    ('audio/mp4', 'AAC'),
)

class MatchModel (models.Model):
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=200, db_index=True, editable=False)
    match_name = models.CharField(max_length=200, db_index=True, editable=False)
    musicbrainz_id = models.CharField(max_length=40, db_index=True, blank=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.name

    def save(self, **kwargs):
        self.slug = slugify(self.name)
        self.match_name = slugify(self.name, strip_words=True)
        super(MatchModel, self).save(**kwargs)

class Artist (MatchModel):
    pass

class Album (MatchModel):
    artist = models.ForeignKey(Artist, related_name='albums', null=True, blank=True)
    num_tracks = models.IntegerField(default=0)
    artwork_path = models.TextField(editable=False)
    release_date = models.DateField(null=True, blank=True)

    def artwork_url(self):
        if self.artwork_path:
            return artwork_storage.url(self.artwork_path)
        return '%simg/cover-default.jpg' % settings.STATIC_URL

class Genre (MatchModel):
    pass

class Track (MatchModel):
    owner = models.ForeignKey(User, related_name='tracks')
    # Audio information
    length = models.FloatField(editable=False)
    bitrate = models.IntegerField(editable=False)
    sample_rate = models.IntegerField(editable=False)
    # Tagging
    artist = models.ForeignKey(Artist, related_name='tracks', null=True, blank=True)
    album = models.ForeignKey(Album, related_name='tracks', null=True, blank=True)
    genre = models.ForeignKey(Genre, related_name='tracks', null=True, blank=True)
    track_number = models.IntegerField(default=0)
    # File information
    file_path = models.TextField(editable=False)
    file_size = models.IntegerField(editable=False)
    file_managed = models.BooleanField(editable=False)
    file_type = models.CharField(max_length=100, choices=FILE_TYPE_CHOICES, editable=False)
    # System information
    date_added = models.DateTimeField(default=timezone.now, editable=False)
    date_modified = models.DateTimeField(editable=False)
    # Other stuff
    play_count = models.IntegerField(default=0, editable=False)

    def save(self, **kwargs):
        self.date_modified = timezone.now()
        super(Track, self).save(**kwargs)

    def url(self):
        if self.file_managed:
            return library_storage.url(self.file_path)
        else:
            return reverse('track-stream', kwargs={'track_id': self.pk})
