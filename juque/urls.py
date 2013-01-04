from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from juque.library.api import TrackResource, ArtistResource, AlbumResource, GenreResource
from juque.playlists.api import PlaylistResource, LivePlaylistResource
from tastypie.api import Api

admin.autodiscover()

urlpatterns = patterns('juque.library.views',
    url(r'^$', 'index', name='index'),
    url(r'^play/(?P<track_id>\d+)/$', 'track_play', name='play'),
    url(r'^playlist/(?P<track_id>\d+)/$', 'track_playlist', name='playlist'),
    url(r'^key/(?P<track_id>\d+)/$', 'track_key', name='key'),
    url(r'^admin/', include(admin.site.urls)),
)

api = Api(api_name='v1')
api.register(ArtistResource())
api.register(AlbumResource())
api.register(GenreResource())
api.register(TrackResource())
api.register(PlaylistResource())
api.register(LivePlaylistResource())

urlpatterns += patterns('',
    url(r'^api/', include(api.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
    )
