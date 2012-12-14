from django.shortcuts import get_object_or_404, render
from django.conf import settings
from django.http import HttpResponse
from django.contrib.sites.models import Site
from juque.library.models import Track
import binascii

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
    proto = 'http' if request.is_secure() else 'http'
    base_url = '%s://%s' % (proto, Site.objects.get_current().domain)
    return render(request, 'playlist.m3u8', {
        'track': track,
        'base_url': base_url,
    }, content_type='application/x-mpegURL')

def track_key(request, track_id):
    track = get_object_or_404(Track, pk=track_id)
    return HttpResponse(binascii.unhexlify(track.aes_key), content_type='application/octet-stream')
