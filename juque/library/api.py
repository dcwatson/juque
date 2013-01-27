from django.db.models import Count
from tastypie.resources import ModelResource
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie import fields
from juque.library.models import Track, Artist, Album, Genre

from django.core.serializers import json
from django.utils import simplejson
from tastypie.serializers import Serializer

class PrettyJSONSerializer (Serializer):
    def to_json(self, data, options=None):
        data = self.to_simple(data, options or {})
        return simplejson.dumps(data, cls=json.DjangoJSONEncoder, sort_keys=True, ensure_ascii=False, indent=4)

class ArtistResource (ModelResource):
    class Meta:
        queryset = Artist.objects.all()
        serializer = PrettyJSONSerializer()
        filtering = {
            'id': ('exact',),
        }

class AlbumResource (ModelResource):
    artwork_url = fields.CharField(attribute='artwork_url')

    class Meta:
        queryset = Album.objects.all()
        serializer = PrettyJSONSerializer()

class GenreResource (ModelResource):
    class Meta:
        queryset = Genre.objects.all()
        serializer = PrettyJSONSerializer()

class TrackResource (ModelResource):
    artist = fields.ForeignKey(ArtistResource, 'artist', null=True, full=True)
    album = fields.ForeignKey(AlbumResource, 'album', null=True, full=True)
    genre = fields.ForeignKey(GenreResource, 'genre', null=True, full=True)
    url = fields.CharField(attribute='url')

    class Meta:
        queryset = Track.objects.select_related('artist', 'album', 'genre')
        excludes = ('file_managed', 'file_path')
        serializer = PrettyJSONSerializer()
        filtering = {
            'artist': ALL_WITH_RELATIONS,
        }
