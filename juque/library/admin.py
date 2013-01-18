from django.contrib import admin
from juque.library.models import Track, Artist, Album, Genre

class TrackAdmin (admin.ModelAdmin):
    list_display = ('name', 'artist', 'album', 'genre', 'length', 'track_number', 'track_date', 'bitrate', 'sample_rate')
    ordering = ('artist', 'name')
    readonly_fields = [f.name for f in Track._meta.fields if not f.editable]

class ArtistAdmin (admin.ModelAdmin):
    list_display = ('name', 'match_name', 'slug')
    ordering = ('name',)

class AlbumAdmin (admin.ModelAdmin):
    list_display = ('name', 'match_name', 'slug', 'artist')
    ordering = ('name',)

class GenreAdmin (admin.ModelAdmin):
    list_display = ('name', 'match_name', 'slug')
    ordering = ('name',)

admin.site.register(Track, TrackAdmin)
admin.site.register(Artist, ArtistAdmin)
admin.site.register(Album, AlbumAdmin)
admin.site.register(Genre, GenreAdmin)
