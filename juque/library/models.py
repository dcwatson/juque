from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.text import slugify as django_slugify
from juque.core.models import User
import os
import re

library_storage = FileSystemStorage(location=settings.MEDIA_ROOT, base_url=settings.MEDIA_URL)

# TODO: This list should probably be shortened. I will need to tweak it after experimenting with a larger sample.
UNIMPORTANT_WORDS = ('a', 'an', 'be', 'and', 'in', 'is', 'it', 'of', 'on', 'or', 'so', 'the', 'to')

FILE_TYPE_CHOICES = (
    ('audio/mp3', 'MP3'),
    ('audio/mp4', 'AAC'),
)

def slugify(name, strip_words=False, strip_parens=True):
    name = name.lower()
    if strip_parens:
        name = re.sub(r'\([^\)]*\)', '', name)
    if strip_words:
        name = re.sub(r'\b(%s)\b' % '|'.join(UNIMPORTANT_WORDS), '', name)
    return django_slugify(name)

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
            return library_storage.url(self.artwork_path)
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
    file_managed = models.BooleanField()
    file_type = models.CharField(max_length=100, choices=FILE_TYPE_CHOICES)
    # System information
    date_added = models.DateTimeField(default=timezone.now, editable=False)
    date_modified = models.DateTimeField(editable=False)
    # Other stuff
    play_count = models.IntegerField(default=0)

    def save(self, **kwargs):
        self.date_modified = timezone.now()
        super(Track, self).save(**kwargs)

    def url(self):
        return library_storage.url(self.file_path)
