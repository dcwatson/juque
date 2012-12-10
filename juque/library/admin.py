from django.contrib import admin
from juque.library.models import Track, Segment, Artist, Album, Genre

class SegmentInline (admin.TabularInline):
    model = Segment

class TrackAdmin (admin.ModelAdmin):
    list_display = ('name', 'artist', 'album', 'genre', 'length', 'bitrate', 'sample_rate')
    ordering = ('artist', 'name')
    inlines = [SegmentInline]

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
