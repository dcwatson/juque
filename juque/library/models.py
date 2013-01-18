from django.db import models
from django.utils import timezone
from django.conf import settings
from django.template.defaultfilters import slugify as django_slugify
from juque.core.models import User
import os
import re

# TODO: This list should probably be shortened. I will need to tweak it after experimenting with a larger sample.
UNIMPORTANT_WORDS = ('a', 'an', 'be', 'and', 'in', 'is', 'it', 'of', 'on', 'or', 'so', 'the', 'to')

def slugify(name, strip_words=False):
    name = name.lower()
    if strip_words:
        name = re.sub(r'\b(%s)\b' % '|'.join(UNIMPORTANT_WORDS), '', name)
    return django_slugify(name)

class MatchModel (models.Model):
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=200, db_index=True, editable=False)
    match_name = models.CharField(max_length=200, db_index=True, editable=False)

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
    track_date = models.CharField(max_length=50, blank=True)
    # File information
    file_path = models.TextField(editable=False)
    file_size = models.IntegerField(editable=False)
    # Cover Art
    cover_path = models.TextField(editable=False)
    # Segment information (optional)
    segment_aes_key = models.CharField(max_length=32, editable=False, blank=True)
    segment_aes_iv = models.CharField(max_length=32, editable=False, blank=True)
    # System information
    date_added = models.DateTimeField(default=timezone.now, editable=False)
    date_modified = models.DateTimeField(editable=False)
    # Other stuff
    play_count = models.IntegerField(default=0)

    def save(self, **kwargs):
        self.date_modified = timezone.now()
        super(Track, self).save(**kwargs)

    def cover_url(self):
        if not self.cover_path:
            return '%simg/cover-default.jpg' % settings.STATIC_URL
        storage = self.owner.get_storage()
        return storage.url(self.cover_path)

    def url(self):
        if settings.DEBUG:
            return '/player/stream/%s/' % self.pk
        else:
            storage = self.owner.get_storage()
            return storage.url(self.file_path)

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
