from django.core.serializers import json
from django.utils import simplejson
from tastypie.resources import ModelResource
from tastypie.serializers import Serializer
from tastypie import fields
from juque.library.models import Track, Artist, Album, Genre

class PrettyJSONSerializer (Serializer):
    json_indent = 2

    def to_json(self, data, options=None):
        options = options or {}
        data = self.to_simple(data, options)
        return simplejson.dumps(data, cls=json.DjangoJSONEncoder, sort_keys=True, ensure_ascii=False, indent=self.json_indent)

class ArtistResource (ModelResource):
    class Meta:
        queryset = Artist.objects.all()
        serializer = PrettyJSONSerializer()

class AlbumResource (ModelResource):
    class Meta:
        queryset = Album.objects.all()
        serializer = PrettyJSONSerializer()

class GenreResource (ModelResource):
    class Meta:
        queryset = Genre.objects.all()
        serializer = PrettyJSONSerializer()

class TrackResource (ModelResource):
    artist = fields.ForeignKey(ArtistResource, 'artist', full=True)
    album = fields.ForeignKey(AlbumResource, 'album', full=True)
    genre = fields.ForeignKey(GenreResource, 'genre', full=True)

    class Meta:
        queryset = Track.objects.all()
        serializer = PrettyJSONSerializer()
        excludes = ('segment_aes_key', 'segment_aes_iv')
