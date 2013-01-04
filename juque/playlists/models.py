from django.db import models
from django.utils import timezone
from juque.library.models import Track
import json

class BasePlaylist (models.Model):
    date_created = models.DateTimeField(default=timezone.now, editable=False)
    date_modified = models.DateTimeField(editable=False)

    class Meta:
        abstract = True

    def save(self, **kwargs):
        self.date_modified = timezone.now()
        super(BasePlaylist, self).save(**kwargs)

    def get_tracks(self):
        raise NotImplementedError()

class Playlist (BasePlaylist):
    name = models.CharField(max_length=200)
    tracks = models.ManyToManyField(Track, through='PlaylistTrack', related_name='playlists')

    def get_tracks(self):
        qs = Track.objects.filter(playlist_tracks__playlist=self).order_by('playlist_tracks__order').select_related('artist', 'album', 'genre')
        return list(qs)

class PlaylistTrack (models.Model):
    playlist = models.ForeignKey(Playlist, related_name='playlist_tracks')
    track = models.ForeignKey(Track, related_name='playlist_tracks')
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ('order',)

class LivePlaylist (BasePlaylist):
    name = models.CharField(max_length=200)
    criteria = models.TextField(blank=True)
    ordering = models.CharField(max_length=100)
    limit = models.IntegerField(default=0)

    def get_tracks(self):
        orders = json.loads(self.ordering)
        qs = Track.objects.order_by(*orders).select_related('artist', 'album', 'genre')
        if self.criteria:
            crit = json.loads(self.criteria)
            qs = qs.filter(**crit)
        if self.limit:
            qs = qs[:self.limit]
        return list(qs)
