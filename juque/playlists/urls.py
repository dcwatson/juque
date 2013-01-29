from django.conf import settings
from django.conf.urls import patterns, include, url

urlpatterns = patterns('juque.playlists.views',
    url(r'^$', 'index', name='playlists'),
    url(r'^(?P<playlist_id>\d+)/edit/$', 'playlist_edit', name='playlist-edit'),
    url(r'^ajax/tracks/$', 'ajax_tracks', name='ajax-tracks'),
)
