from django.conf import settings
from django.conf.urls import patterns, include, url

urlpatterns = patterns('juque.player.views',
    url(r'^(?P<track_id>\d+)/$', 'track_play', name='play'),
    url(r'^stream/(?P<track_id>\d+)/$', 'track_stream', name='stream'),
    url(r'^transcode/(?P<track_id>\d+)/(?P<codec>\w+)/$', 'track_transcode', name='transcode'),
)
