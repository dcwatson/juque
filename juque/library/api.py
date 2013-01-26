from django.db.models import Count
from tastypie.resources import ModelResource
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie import fields
from juque.library.models import Track, Artist, Album, Genre

from django.core.serializers import json
from django.utils import simplejson
from tastypie.serializers import Serializer

class PrettyJSONSerializer (Serializer):
    json_indent = 4

    def to_json(self, data, options=None):
        options = options or {}
        data = self.to_simple(data, options)
        return simplejson.dumps(data, cls=json.DjangoJSONEncoder,
                sort_keys=True, ensure_ascii=False, indent=self.json_indent)

class ArtistResource (ModelResource):
    class Meta:
        queryset = Artist.objects.all()
        serializer = PrettyJSONSerializer()
        filtering = {
            'id': ('exact',),
        }

class AlbumResource (ModelResource):
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
