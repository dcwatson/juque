from django.conf import settings
from django.conf.urls import patterns, include, url

urlpatterns = patterns('juque.library.views',
    url(r'^$', 'index', name='library'),
    url(r'^genre/(?P<slug>[a-zA-Z0-9_\-]+)/$', 'genre', name='library-genre'),
    url(r'^user/(?P<uid>\d+)/$', 'user', name='library-user'),
    url(r'^cleanup/artists/$', 'cleanup_artists', name='cleanup-artists'),
    url(r'^cleanup/albums/$', 'cleanup_albums', name='cleanup-albums'),
    url(r'^cleanup/tracks/$', 'cleanup_tracks', name='cleanup-tracks'),
    url(r'^track/(?P<track_id>\d+)/$', 'track_edit', name='track-edit'),
    url(r'^track/stream/(?P<track_id>\d+)\.(?P<extension>\w+)$', 'track_stream', name='track-stream'),
    url(r'^album/(?P<album_id>\d+)/thumbnail/$', 'album_thumbnail', name='album-thumbnail'),
    url(r'^ajax/page/$', 'ajax_page', name='ajax-page'),
)
