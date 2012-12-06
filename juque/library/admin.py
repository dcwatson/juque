from django.contrib import admin
from juque.library.models import Track, Artist, Album, Genre

class TrackAdmin (admin.ModelAdmin):
    list_display = ('name', 'artist', 'album', 'genre', 'length', 'bitrate', 'sample_rate')
    ordering = ('artist', 'name')

class ArtistAdmin (admin.ModelAdmin):
    list_display = ('name', 'match_name')
    ordering = ('name',)

class AlbumAdmin (admin.ModelAdmin):
    list_display = ('name', 'match_name', 'artist')
    ordering = ('name',)

class GenreAdmin (admin.ModelAdmin):
    list_display = ('name', 'match_name')
    ordering = ('name',)

admin.site.register(Track, TrackAdmin)
admin.site.register(Artist, ArtistAdmin)
admin.site.register(Album, AlbumAdmin)
admin.site.register(Genre, GenreAdmin)
