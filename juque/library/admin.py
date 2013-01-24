from django.contrib import admin
from juque.library.models import Track, Artist, Album, Genre

class TrackAdmin (admin.ModelAdmin):
    list_display = ('name', 'match_name', 'slug', 'file_type', 'artist', 'album', 'genre', 'length', 'track_number',
        'bitrate', 'sample_rate', 'musicbrainz_id')
    list_filter = ('file_type',)
    ordering = ('artist', 'album', 'name')
    readonly_fields = [f.name for f in Track._meta.fields if not f.editable]

class ArtistAdmin (admin.ModelAdmin):
    list_display = ('name', 'match_name', 'slug', 'musicbrainz_id')
    ordering = ('name',)

class AlbumAdmin (admin.ModelAdmin):
    list_display = ('name', 'match_name', 'slug', 'artist', 'release_date', 'num_tracks', 'musicbrainz_id')
    date_hierarchy = 'release_date'
    ordering = ('artist', 'name')

class GenreAdmin (admin.ModelAdmin):
    list_display = ('name', 'match_name', 'slug')
    ordering = ('name',)

admin.site.register(Track, TrackAdmin)
admin.site.register(Artist, ArtistAdmin)
admin.site.register(Album, AlbumAdmin)
admin.site.register(Genre, GenreAdmin)
