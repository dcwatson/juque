from django.shortcuts import get_object_or_404, render
from django.conf import settings
from django.http import HttpResponse
from django.contrib.sites.models import Site
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count
from django.db import connections
from juque.library.models import Track, Artist, Album, Genre
from bootstrap.utils import local_page_range
import collections
import binascii

def index(request, genre=None):
    q = request.GET.get('q', '').strip()
    qs = Track.objects.select_related('artist', 'album').order_by('artist__name', 'album__name', 'name')
    if genre:
        qs = qs.filter(genre=genre)
    if q:
        q_obj = Q(name__icontains=q) | Q(artist__name__icontains=q) | Q(album__name__icontains=q)
        qs = qs.filter(q_obj)
    paginator = Paginator(qs, 15)
    try:
        page = paginator.page(request.GET.get('page'))
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    genres = Genre.objects.annotate(num_tracks=Count('tracks')).order_by('-num_tracks')[:10]
    return render(request, 'library/index.html', {
        'page': page,
        'page_range': local_page_range(page, 15),
        'q': q,
        'genres': genres,
    })

def genre(request, slug):
    genre = get_object_or_404(Genre, slug=slug)
    return index(request, genre=genre)

def cleanup_artists(request):
    if request.method == 'POST':
        artist_map = {}
        for name, artist_id in request.POST.items():
            try:
                artist = Artist.objects.get(pk=artist_id)
                artist_map[name] = artist
            except:
                pass
        for match_name, artist in artist_map.items():
            Track.objects.filter(artist__match_name=match_name).exclude(artist=artist).update(artist=artist)
            Album.objects.filter(artist__match_name=match_name).exclude(artist=artist).update(artist=artist)
            Artist.objects.filter(match_name=match_name).exclude(pk=artist.pk).delete()
    cursor = connections['default'].cursor()
    cursor.execute("""
        select a.match_name
        from library_artist a
        group by a.match_name
        having count(a.id) > 1
    """)
    match_names = [r[0] for r in cursor.fetchall()]
    cursor.close()
    groups = collections.OrderedDict()
    for a in Artist.objects.filter(match_name__in=match_names).annotate(num_tracks=Count('tracks__pk')).order_by('match_name', '-num_tracks'):
        if a.match_name not in groups:
            groups[a.match_name] = []
        groups[a.match_name].append(a)
    return render(request, 'library/cleanup_artists.html', {
        'artist_groups': groups,
    })

def cleanup_albums(request):
    if request.method == 'POST':
        fixes = []
        for key, album_id in request.POST.items():
            try:
                artist_id, name = key.split('|', 1)
                album = Album.objects.get(pk=album_id)
                fixes.append((int(artist_id), name, album))
            except:
                pass
        for artist_id, match_name, album in fixes:
            Track.objects.filter(album__artist__pk=artist_id, album__match_name=match_name).exclude(album=album).update(album=album)
            Album.objects.filter(artist__pk=artist_id, match_name=match_name).exclude(pk=album.pk).delete()
    cursor = connections['default'].cursor()
    cursor.execute("""
        select a.artist_id, a.match_name
        from library_album a
        group by a.artist_id, a.match_name
        having count(a.id) > 1
    """)
    dupes = []
    for row in cursor.fetchall():
        artist = Artist.objects.get(pk=row[0])
        albums = Album.objects.filter(artist=artist, match_name=row[1]).annotate(num_tracks=Count('tracks')).order_by('-num_tracks')
        dupes.append({
            'artist': artist,
            'albums': albums,
            'match_name': row[1],
            'key': '%s|%s' % (row[0], row[1]),
        })
    return render(request, 'library/cleanup_albums.html', {
        'album_dupes': dupes,
    })

def cleanup_tracks(request):
    # TODO: could include album as part of the dupe-checking, but it would catch as many
    # TODO: could probably also refactor/combine this and cleanup_albums quite a bit
    if request.method == 'POST':
        fixes = []
        for key, track_id in request.POST.items():
            try:
                artist_id, name = key.split('|', 1)
                track = Track.objects.get(pk=track_id)
                fixes.append((int(artist_id), name, track))
            except:
                pass
        for artist_id, match_name, track in fixes:
            Track.objects.filter(artist__pk=artist_id, match_name=match_name).exclude(pk=track.pk).delete()
    cursor = connections['default'].cursor()
    cursor.execute("""
        select t.artist_id, t.match_name
        from library_track t
        group by t.artist_id, t.match_name
        having count(t.id) > 1
    """)
    dupes = []
    for row in cursor.fetchall():
        artist = Artist.objects.get(pk=row[0])
        tracks = Track.objects.filter(artist=artist, match_name=row[1]).select_related('album').order_by('-bitrate', '-length')
        dupes.append({
            'artist': artist,
            'tracks': tracks,
            'match_name': row[1],
            'key': '%s|%s' % (row[0], row[1]),
        })
    return render(request, 'library/cleanup_tracks.html', {
        'track_dupes': dupes,
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
