from tastypie.resources import ModelResource
from tastypie import fields
from juque.library.models import Track, Artist, Album, Genre

class ArtistResource (ModelResource):
    class Meta:
        queryset = Artist.objects.all()

class AlbumResource (ModelResource):
    class Meta:
        queryset = Album.objects.all()

class GenreResource (ModelResource):
    class Meta:
        queryset = Genre.objects.all()

class TrackResource (ModelResource):
    artist = fields.ForeignKey(ArtistResource, 'artist', full=True)
    album = fields.ForeignKey(AlbumResource, 'album', full=True)
    genre = fields.ForeignKey(GenreResource, 'genre', full=True)

    class Meta:
        queryset = Track.objects.all()
        excludes = ('segment_aes_key', 'segment_aes_iv')
