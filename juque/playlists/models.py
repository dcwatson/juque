from django.db import models
from django.utils import timezone
from juque.core.models import User
from juque.library.models import Track
import json

class BasePlaylist (models.Model):
    owner = models.ForeignKey(User, related_name='%(class)ss')
    name = models.CharField(max_length=200)
    date_created = models.DateTimeField(default=timezone.now, editable=False)
    date_modified = models.DateTimeField(editable=False)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.name

    def save(self, **kwargs):
        self.date_modified = timezone.now()
        super(BasePlaylist, self).save(**kwargs)

    def queryset(self):
        raise NotImplementedError()

    def get_tracks(self):
        return list(self.queryset())

class Playlist (BasePlaylist):
    tracks = models.ManyToManyField(Track, through='PlaylistTrack', related_name='playlists')

    def queryset(self):
        return Track.objects.filter(playlist_tracks__playlist=self).order_by('playlist_tracks__order').select_related('artist', 'album', 'genre')

class PlaylistTrack (models.Model):
    playlist = models.ForeignKey(Playlist, related_name='playlist_tracks')
    track = models.ForeignKey(Track, related_name='playlist_tracks')
    order = models.IntegerField()

    class Meta:
        ordering = ('order',)
        unique_together = (
            ('playlist', 'track'),
            ('id', 'order'),
        )

class LivePlaylist (BasePlaylist):
    criteria = models.TextField(blank=True)
    ordering = models.CharField(max_length=100)
    limit = models.IntegerField(default=0)

    def queryset(self):
        orders = json.loads(self.ordering)
        qs = Track.objects.order_by(*orders).select_related('artist', 'album', 'genre')
        if self.criteria:
            crit = json.loads(self.criteria)
            qs = qs.filter(**crit)
        if self.limit:
            qs = qs[:self.limit]
