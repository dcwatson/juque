from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('juque.library.views',
    url(r'^$', 'index', name='index'),
    url(r'^play/(?P<track_id>\d+)/$', 'track_play', name='play'),
    url(r'^playlist/(?P<track_id>\d+)/$', 'track_playlist', name='playlist'),
    url(r'^key/(?P<track_id>\d+)/$', 'track_key', name='key'),
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
    )
