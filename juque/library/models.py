from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.files.base import File
from django.core.urlresolvers import reverse
from juque.core.models import User
from juque.library.utils import slugify, library_storage
import mimetypes
import logging
import hashlib
import os
import re

logger = logging.getLogger(__name__)

FILE_TYPE_CHOICES = (
    ('audio/mp3', 'MP3'),
    ('audio/mp4', 'AAC'),
)

FILE_EXTENSIONS = {
    'audio/mp3': 'mp3',
    'audio/mp4': 'm4a',
    'image/jpeg': 'jpg',
    'image/png': 'png',
    'image/gif': 'gif',
}

class MatchModel (models.Model):
    name = models.CharField(max_length=200, db_index=True)
    slug = models.CharField(max_length=200, db_index=True, editable=False)
    match_name = models.CharField(max_length=200, db_index=True, editable=False)
    musicbrainz_id = models.CharField(max_length=40, db_index=True, blank=True)
    scrobbled_name = models.CharField(max_length=200, blank=True, editable=False)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.name

    def save(self, **kwargs):
        self.slug = slugify(self.name)
        self.match_name = slugify(self.name, strip_words=True)
        super(MatchModel, self).save(**kwargs)

class Artist (MatchModel):
    def get_absolute_url(self):
        return reverse('library-artist', kwargs={'slug': self.slug})

class Album (MatchModel):
    artist = models.ForeignKey(Artist, related_name='albums')
    artwork_path = models.TextField(editable=False)
    artwork_type = models.CharField(max_length=100, choices=FILE_TYPE_CHOICES, editable=False)
    total_tracks = models.IntegerField(default=0)
    release_date = models.DateField(null=True, blank=True)

    def get_expected_path(self):
        assert self.pk is not None
        h = hashlib.md5(str(self.pk) + settings.SECRET_KEY).hexdigest()[:2]
        name = '%s.%s' % (self.pk, FILE_EXTENSIONS.get(self.artwork_type, 'dat'))
        return os.path.join('artwork', h, name)

    def artwork_url(self):
        if self.artwork_path:
            return reverse('album-thumbnail', kwargs={'album_id': self.pk})
            #return artwork_storage.url(self.artwork_path)
        return '%simg/cover.png' % settings.STATIC_URL

    def sorted_tracks(self):
        return self.tracks.order_by('track_number', 'name')

class Genre (MatchModel):
    pass

class Track (MatchModel):
    owner = models.ForeignKey(User, related_name='tracks')
    # Audio information
    length = models.FloatField(editable=False)
    bitrate = models.IntegerField(editable=False)
    sample_rate = models.IntegerField(editable=False)
    # Tagging
    artist_name = models.CharField(max_length=200, blank=True)
    album_name = models.CharField(max_length=200, blank=True)
    genre_name = models.CharField(max_length=200, blank=True)
    track_number = models.IntegerField(default=0)
    lyrics = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    # Relations
    artist = models.ForeignKey(Artist, related_name='tracks', null=True, blank=True, editable=False)
    album = models.ForeignKey(Album, related_name='tracks', null=True, blank=True, editable=False)
    genre = models.ForeignKey(Genre, related_name='tracks', null=True, blank=True, editable=False)
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

    def get_expected_path(self):
        assert self.pk is not None
        h = hashlib.md5(str(self.pk) + settings.SECRET_KEY).hexdigest()[:2]
        name = '%s.%s' % (self.pk, FILE_EXTENSIONS.get(self.file_type, 'dat'))
        return os.path.join('tracks', h, name)

    def save(self, **kwargs):
        if kwargs.pop('check_relations', True):
            if self.artist_name:
                self.artist, created = Artist.objects.get_or_create(slug=slugify(self.artist_name), defaults={'name': self.artist_name})
                if created:
                    logger.debug('Created new Artist: %s', self.artist)
            else:
                self.artist = None
            if self.artist and self.album_name:
                self.album, created = Album.objects.get_or_create(artist=self.artist, slug=slugify(self.album_name), defaults={'name': self.album_name})
                if created:
                    logger.debug('Created new Album: %s', self.album)
            else:
                self.album = None
            if self.genre_name:
                self.genre, created = Genre.objects.get_or_create(slug=slugify(self.genre_name), defaults={'name': self.genre_name})
                if created:
                    logger.debug('Created new Genre: %s', self.genre)
            else:
                self.genre = None
        self.date_modified = timezone.now()
        super(Track, self).save(**kwargs)

    def url(self):
        if not settings.JUQUE_STORAGE_LOCAL:
            # If the media isn't stored locally, return the URL from the storage.
            return library_storage.url(self.file_path)
        else:
            # Otherwise, we'll use our streaming view.
            ext = os.path.splitext(self.file_path)[1][1:]
            return reverse('track-stream', kwargs={'track_id': self.pk, 'extension': ext})

    def artwork_url(self):
        if self.album:
            return self.album.artwork_url()
        return '%simg/cover.png' % settings.STATIC_URL

class PlayHistory (models.Model):
    track = models.ForeignKey(Track, related_name='play_history')
    user = models.ForeignKey(User, related_name='play_history')
    date_played = models.DateTimeField(default=timezone.now)
