from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db.models import Q
from juque.playlists.models import Playlist
from juque.library.models import Track
from juque.library.templatetags.track import track_length
import json

def index(request):
    return render(request, 'playlists/index.html', {
        'playlists': Playlist.objects.select_related('owner'),
    })

def playlist_form(request, playlist):
    if request.method == 'POST':
        playlist.name = request.POST.get('name', playlist.name).strip()
        playlist.save()
        playlist.playlist_tracks.all().delete()
        for idx, track_id in enumerate(request.POST.getlist('tracks')):
            try:
                track = Track.objects.get(pk=track_id)
                playlist.playlist_tracks.create(track=track, order=idx+1)
            except:
                pass
        return redirect('playlist-edit', playlist_id=playlist.pk)
    return render(request, 'playlists/edit.html', {
        'playlist': playlist,
    })

def playlist_create(request):
    return playlist_form(request, Playlist(owner=request.user, name='Untitled Playlist'))

def playlist_edit(request, playlist_id):
    playlist = get_object_or_404(Playlist, pk=playlist_id)
    return playlist_form(request, playlist)

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
            'pk': t.pk,
            'track': t.name,
            'artist': t.artist.name if t.artist else None,
            'album': t.album.name if t.album else None,
            'length': track_length(t.length),
        })
    return HttpResponse(json.dumps(info), content_type='application/json')
