from tastypie.resources import ModelResource
from juque.playlists.models import Playlist, LivePlaylist
from juque.library.api import TrackResource

class PlaylistTracksMixIn (object):
    def alter_detail_data_to_serialize(self, request, data):
        res = TrackResource()
        track_data = []
        for track in data.obj.get_tracks():
            b = res.full_dehydrate(res.build_bundle(obj=track))
            track_data.append(b.data)
        data.data['tracks'] = track_data
        return data

class PlaylistResource (PlaylistTracksMixIn, ModelResource):
    class Meta:
        queryset = Playlist.objects.all()

class LivePlaylistResource (PlaylistTracksMixIn, ModelResource):
    class Meta:
        queryset = LivePlaylist.objects.all()
