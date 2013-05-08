from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
from django.http import HttpResponse
from django.contrib.sites.models import Site
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count, Sum, F
from django.db import connections
from juque.core.models import User
from juque.library.models import Track, Artist, Album, Genre
from juque.library.forms import TrackForm, common_form_factory
from juque.library.utils import RangeFileWrapper, render_thumbnail, get_query_html
from juque.playlists.models import Playlist
from bootstrap.utils import local_page_range
from wsgiref.util import FileWrapper
import collections
import binascii
import json
import re

range_re = re.compile(r'bytes\s*=\s*(\d+)\s*-\s*(\d*)', re.I)

EDIT_FIELDS = (
    ('name', 'Track Name', Track),
    ('artist__name', 'Artist', Artist),
    ('album__name', 'Album', Album),
    ('genre__name', 'Genre', Genre),
)

@login_required
def ajax_play(request, track_id):
    track = get_object_or_404(Track, pk=track_id)
    track.play_history.create(user=request.user)
    Track.objects.filter(pk=track.pk).update(play_count=F('play_count') + 1)
    return HttpResponse('OK')

@login_required
def ajax_query(request):
    query = request.GET.get('q', '').strip()
    results = []
    for artist in Artist.objects.filter(name__icontains=query).order_by('name')[:3]:
        results.append({
            'type': 'artist',
            'name': artist.name,
            'url': artist.get_absolute_url(),
            'id': artist.pk,
            'html': get_query_html(artist, query),
        })
    q_obj = Q(name__icontains=query) | Q(artist__name__icontains=query) | Q(album__name__icontains=query)
    for track in Track.objects.filter(q_obj).select_related('artist', 'album').order_by('name')[:5]:
        results.append({
            'type': 'track',
            'name': track.name,
            'artist': track.artist.name if track.artist else None,
            'album': track.album.name if track.album else None,
            'url': track.url(),
            'artwork_url': track.artwork_url(),
            'id': track.pk,
            'html': get_query_html(track, query),
        })
    return HttpResponse(json.dumps(results, indent=4), content_type='application/json')

@login_required
def ajax_page(request):
    query = request.GET.get('q', '').strip()
    genre_id = request.GET.get('g', '').strip()
    user_id = request.GET.get('u', '').strip()
    try:
        page_num = int(request.GET['p'])
    except:
        page_num = 1
    qs = Track.objects.select_related('artist', 'album').order_by('artist__name', 'album__name', 'name')
    if genre_id:
        qs = qs.filter(genre__pk=genre_id)
    if user_id:
        qs = qs.filter(owner__pk=user_id)
    if query:
        q_obj = Q(name__icontains=query) | Q(artist__name__icontains=query) | Q(album__name__icontains=query)
        qs = qs.filter(q_obj)
    paginator = Paginator(qs, 20)
    try:
        page = paginator.page(page_num)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    return render(request, 'library/page.html', {
        'page': page,
        'page_range': local_page_range(page, 11),
        'query': {
            'q': query,
            'u': user_id,
            'g': genre_id,
        },
        'playlists': list(Playlist.objects.all()),
    })

@login_required
def ajax_autocomplete(request):
    query = request.GET.get('q', '').strip()
    field = request.GET.get('f', '').strip()
    values = []
    for field_path, field_label, model_class in EDIT_FIELDS:
        if field_path == field:
            field_name = str(field_path.split('__')[-1])
            q = {'%s__icontains' % field_name: query}
            values = list(model_class.objects.values_list(field_name, flat=True).distinct().filter(**q).order_by(field_name))
    return HttpResponse(json.dumps(values), content_type='applcation/json')

@login_required
def index(request, genre=None, owner=None):
    return render(request, 'library/index.html', {
        'q': request.GET.get('q', '').strip(),
        'genres': Genre.objects.annotate(num_tracks=Count('tracks')).order_by('-num_tracks')[:10],
        'users': User.objects.annotate(num_tracks=Count('tracks')).order_by('-num_tracks'),
    })

@login_required
def stats(request):
    return render(request, 'library/stats.html', {
        'total': Track.objects.aggregate(tracks=Count('id'), length=Sum('length'), file_size=Sum('file_size')),
        'added': Track.objects.select_related('artist').order_by('-date_added', '-id')[:10],
        'artists': Artist.objects.annotate(num_tracks=Count('tracks')).order_by('-num_tracks')[:10],
        'played': Track.objects.filter(play_count__gt=0).select_related('artist').order_by('-play_count')[:10],
    })

@login_required
def artist(request, slug):
    artist = get_object_or_404(Artist, slug=slug)
    return render(request, 'library/artist.html', {
        'artist': artist,
    })

@login_required
def genre(request, slug):
    genre = get_object_or_404(Genre, slug=slug)
    return index(request, genre=genre)

@login_required
def user(request, uid):
    owner = get_object_or_404(User, pk=uid)
    return index(request, owner=owner)

def album_thumbnail(request, album_id):
    album = get_object_or_404(Album, pk=album_id)
    data = render_thumbnail(album)
    return HttpResponse(data, content_type='image/png')

@login_required
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

@login_required
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
        albums = Album.objects.filter(artist=artist, match_name=row[1]).annotate(num_tracks_local=Count('tracks')).order_by('-num_tracks_local')
        dupes.append({
            'artist': artist,
            'albums': albums,
            'match_name': row[1],
            'key': '%s|%s' % (row[0], row[1]),
        })
    return render(request, 'library/cleanup_albums.html', {
        'album_dupes': dupes,
    })

@login_required
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

def track_stream(request, track_id, extension):
    track = get_object_or_404(Track, pk=track_id)
    if track.file_managed:
        return HttpResponse('Cannot stream this track.', status=500)
    fp = open(track.file_path, 'rb')
    range_header = request.META.get('HTTP_RANGE', '').strip()
    range_match = range_re.match(range_header)
    if range_match:
        start, end = range_match.groups()
        start = int(start) if start else 0
        end = int(end) if end else track.file_size - 1
        if end >= track.file_size:
            end = track.file_size - 1
        length = end - start + 1
        resp = HttpResponse(RangeFileWrapper(fp, offset=start, length=length), status=206, content_type=track.file_type)
        resp['Content-Length'] = str(length)
        resp['Content-Range'] = 'bytes %s-%s/%s' % (start, end, track.file_size)
    else:
        resp = HttpResponse(FileWrapper(fp), content_type=track.file_type)
        resp['Content-Length'] = str(track.file_size)
    resp['Accept-Ranges'] = 'bytes'
    return resp

@login_required
def track_edit(request, track_id):
    track = get_object_or_404(Track.objects.select_related('artist', 'album', 'genre'), pk=track_id)
    return render(request, 'library/track_edit.html', {
        'track': track,
        'form': TrackForm(instance=track),
    })

@login_required
def track_multi_edit(request):
    tracks = Track.objects.filter(pk__in=request.REQUEST.getlist('t'))
    form_class = common_form_factory(tracks, EDIT_FIELDS)
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse('OK')
    else:
        form = form_class()
    return render(request, 'library/track_multi.html', {
        'form': form,
        'tracks': tracks,
    })

def track_play(request, track_id):
    track = get_object_or_404(Track, pk=track_id)
    return render(request, 'track.html', {
        'track': track,
    })
