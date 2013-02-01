from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from juque.library.api import TrackResource, ArtistResource, AlbumResource, GenreResource
from juque.playlists.api import PlaylistResource, LivePlaylistResource
from tastypie.api import Api

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'juque.core.views.home', name='home'),
    url(r'^login/$', 'juque.core.views.login', name='login'),
    url(r'^logout/$', 'juque.core.views.logout', name='logout'),
    url(r'^library/', include('juque.library.urls')),
    url(r'^playlists/', include('juque.playlists.urls')),
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
