from django.shortcuts import get_object_or_404, render
from django.conf import settings
from django.http import HttpResponse
from juque.library.models import Track

def index(request):
    return render(request, 'index.html', {
        'tracks': Track.objects.order_by('artist__name', 'name'),
    })

def track_play(request, track_id):
    track = get_object_or_404(Track, pk=track_id)
    return render(request, 'track.html', {
        'track': track,
    })

def track_playlist(request, track_id):
    track = get_object_or_404(Track, pk=track_id)
    base_url = 'http://localhost:8000' # TODO: Sites? S3?
    return render(request, 'playlist.m3u8', {
        'track': track,
        'base_url': base_url,
    }, content_type='application/x-mpegURL')

def track_key(request, track_id):
    track = get_object_or_404(Track, pk=track_id)
    data = ''
    for i in range(16):
        data += chr(int(track.aes_key[i*2:(i*2)+2], 16))
    return HttpResponse(data, content_type='application/octet-stream')
