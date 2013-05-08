from django.conf import settings
from django.conf.urls import patterns, include, url

urlpatterns = patterns('juque.playlists.views',
    url(r'^$', 'index', name='playlists'),
    url(r'^new/$', 'playlist_create', name='playlist-create'),
    url(r'^(?P<playlist_id>\d+)/edit/$', 'playlist_edit', name='playlist-edit'),
    url(r'^(?P<playlist_id>\d+)/download/(?P<file_format>\w+)/$', 'playlist_download', name='playlist-download'),
    url(r'^ajax/tracks/$', 'ajax_tracks', name='ajax-tracks'),
    url(r'^ajax/add/$', 'ajax_add', name='ajax-playlist-add'),
)
