from django.conf import settings
from django.conf.urls import patterns, include, url

urlpatterns = patterns('juque.library.views',
    url(r'^$', 'index', name='library'),
    url(r'^genre/(?P<slug>[a-zA-Z0-9_\-]+)/$', 'genre', name='genre'),
    url(r'^cleanup/artists/$', 'cleanup_artists', name='cleanup-artists'),
    url(r'^cleanup/albums/$', 'cleanup_albums', name='cleanup-albums'),
    url(r'^cleanup/tracks/$', 'cleanup_tracks', name='cleanup-tracks'),
)
