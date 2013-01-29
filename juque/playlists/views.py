from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.db.models import Q
from juque.playlists.models import Playlist
from juque.library.models import Track
from juque.library.templatetags.track import track_length
import json

def index(request):
    return render(request, 'playlists/index.html', {
    })

def playlist_edit(request, playlist_id):
    playlist = get_object_or_404(Playlist, pk=playlist_id)
    return render(request, 'playlists/edit.html', {
        'playlist': playlist,
    })

def ajax_tracks(request):
    q = request.GET.get('q', '').strip()
    try:
        n = int(request.GET['n'])
    except:
        n = 8
    q_obj = Q(name__icontains=q) | Q(artist__name__icontains=q) | Q(album__name__icontains=q)
    info = []
    for t in Track.objects.filter(q_obj).select_related('artist', 'album').order_by('name')[:n]:
        info.append({
            'track': t.name,
            'artist': t.artist.name if t.artist else None,
            'album': t.album.name if t.album else None,
            'length': track_length(t.length),
        })
    return HttpResponse(json.dumps(info), content_type='application/json')
