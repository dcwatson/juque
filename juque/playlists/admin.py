from django.contrib import admin
from juque.playlists.models import Playlist, PlaylistTrack, LivePlaylist

class TrackInline (admin.TabularInline):
    model = PlaylistTrack

class PlaylistAdmin (admin.ModelAdmin):
    list_display = ('name', 'date_created', 'date_modified')
    inlines = (TrackInline,)
    exclude = ('tracks',)

class LivePlaylistAdmin (admin.ModelAdmin):
    list_display = ('name', 'limit', 'date_created', 'date_modified')

admin.site.register(Playlist, PlaylistAdmin)
admin.site.register(LivePlaylist, LivePlaylistAdmin)
