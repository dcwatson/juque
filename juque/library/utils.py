from django.conf import settings
from django.core.files.base import File, ContentFile
from django.core.files.storage import get_storage_class
from django.core.cache import cache
from django.utils.text import slugify as django_slugify
from django.template import loader
from django import forms
from juque.core.models import User
from juque.lastfm import get_album_info, get_album_artwork, get_track_info
from mutagen import id3, mp4, File as scan_file
from PIL import Image
from StringIO import StringIO
import mimetypes
import datetime
import requests
import logging
import re
import os

logger = logging.getLogger(__name__)

# Build library storage backend.
library_storage = get_storage_class(settings.JUQUE_STORAGE['backend'])(**settings.JUQUE_STORAGE['options'])

# TODO: This list should probably be shortened. I will need to tweak it after experimenting with a larger sample.
UNIMPORTANT_WORDS = ('a', 'an', 'be', 'and', 'in', 'is', 'it', 'of', 'on', 'or', 'so', 'the', 'to')

TAG_MAPPERS = {
    id3.ID3: {
        'TPE1': 'artist',
        'TPE2': 'albumartist',
        'TCON': 'genre',
        'TALB': 'album',
        'TIT1': 'grouping',
        'TIT2': 'title',
        'TIT3': 'subtitle',
        'TDRC': 'date',
        'TDOR': 'originaldate',
        'TRCK': 'track',
        'USLT': 'lyrics',
        'COMM': 'notes',
    },
    mp4.MP4Tags: {
        '\xa9ART': 'artist',
        '\xa9nam': 'title',
        '\xa9alb': 'album',
        'aART': 'albumartist',
        '\xa9grp': 'grouping',
        '\xa9day': 'date',
        '\xa9gen': 'genre',
        '\xa9lyr': 'lyrics',
        '\xa9cmt': 'notes',
        'trkn': 'track',
    }
}

def slugify(name, strip_words=False, strip_parens=True):
    name = unicode(name).lower()
    if strip_parens:
        name = re.sub(r'\([^\)]*\)', '', name)
    if strip_words:
        name = re.sub(r'\b(%s)\b' % '|'.join(UNIMPORTANT_WORDS), '', name)
    return django_slugify(name)

def map_tags(tags):
    mapper = TAG_MAPPERS[tags.__class__]
    mapped_tags = {}
    for key, value in tags.items():
        if isinstance(value, (list, tuple)):
            value = value[0]
        if key in mapper:
            mapped_tags[mapper[key]] = unicode(value).strip().replace('\x00', '')
    return mapped_tags

def extract_artwork(tags):
    if isinstance(tags, mp4.MP4Tags):
        cover = tags['covr'][0]
        if cover.imageformat == mp4.MP4Cover.FORMAT_JPEG:
            return 'image/jpeg', cover
        elif cover.imageformat == mp4.MP4Cover.FORMAT_PNG:
            return 'image/png', cover
        raise ValueError('Unknown image format.')
    elif isinstance(tags, id3.ID3):
        cover = tags['APIC:']
        if cover.type == 3:
            return cover.mime, cover.data
        raise ValueError('Artwork was no front cover art.')
    raise ValueError('No artwork found.')

def retag_track(track):
    tags = scan_file(track.file_path).tags
    mapper = TAG_MAPPERS[tags.__class__]
    tags.clear()
    for tag, name in mapper.items():
        if name == 'artist':
            tags[tag] = track.artist.name
        elif name == 'title':
            tags[tag] = track.name
        elif name == 'album':
            tags[tag] = track.album.name
        elif name == 'genre':
            tags[tag] = track.genre.name
    tags.save(track.file_path)

def update_album(album, autocorrect=True):
    info = get_album_info(album.artist.name, album.name, autocorrect=autocorrect)
    if 'name' in info:
        album.scrobbled_name = info['name']
    if 'mbid' in info:
        album.musicbrainz_id = info['mbid']
    try:
        s = info['releasedate'].strip().split(',')[0]
        album.release_date = datetime.datetime.strptime(s, '%d %b %Y').date()
    except:
        pass
    if 'artist' in info:
        album.artist.scrobbled_name = info['artist']
    if 'tracks' in info and 'track' in info['tracks'] and isinstance(info['tracks']['track'], (list, tuple)):
        album.total_tracks = len(info['tracks']['track'])
        track_info = {}
        for t in info['tracks']['track']:
            if 'artist' in t and t['artist']['mbid'] and album.artist.scrobbled_name == t['artist']['name']:
                album.artist.musicbrainz_id = t['artist']['mbid']
            match = slugify(t['name'], strip_words=True)
            # Only store the first matching track information. Sometimes the later matches are LP versions and such.
            # Maybe someday, investigate how to better match tracks (duration, fuzzy name, etc).
            if match not in track_info:
                track_info[match] = t
        for track in album.tracks.filter(match_name__in=track_info.keys()):
            t = track_info[track.match_name]
            track.scrobbled_name = t['name']
            if 'mbid' in t:
                track.musicbrainz_id = t['mbid']
            if '@attr' in t and 'rank' in t['@attr']:
                track.track_number = int(t['@attr']['rank'])
            track.save(check_relations=False)
    if not album.artwork_path and 'image' in info:
        image_urls = {}
        for i in info['image']:
            image_urls[i['size']] = i['#text']
        # Try to get the largest album artwork we can.
        for s in ('mega', 'extralarge', 'large', 'medium', 'small'):
            try:
                r = requests.get(image_urls[s])
                mime = r.headers['Content-Type'].split(';')[0]
                logger.debug('Downloaded %s for %s', image_urls[s], album)
                # Just save it to the right directory for now, the Album object will move it as necessary.
                path = os.path.join(album.artist.name, album.name, 'artwork.tmp')
                if library_storage.exists(path):
                    library_storage.delete(path)
                    logger.debug('Deleted existing artwork at %s', path)
                album.artwork_type = mime
                album.artwork_path = library_storage.save(path, ContentFile(r.content))
                break
            except:
                pass
    album.artist.save()
    album.save()

def create_track(file_path, owner, copy=None):
    from juque.library.models import Track
    if copy is None:
        copy = settings.JUQUE_COPY_SOURCE
    file_size = os.path.getsize(file_path)
    meta = scan_file(file_path)
    if not meta or not meta.tags:
        logger.warning('No tags found in %s; Skipping.', file_path)
        return
    tags = map_tags(meta.tags)
    # Sometimes the track number is a number, sometimes it's a string like "2 / 13"
    track_number = 0
    if 'track' in tags:
        if tags['track'].isdigit():
            track_number = int(tags['track'])
        elif '/' in tags['track']:
            try:
                track_number = int(tags['track'].split('/')[0])
            except:
                pass
    track = Track.objects.create(
        owner=owner,
        name=tags.get('title', os.path.basename(file_path)),
        length=meta.info.length,
        bitrate=meta.info.bitrate,
        sample_rate=meta.info.sample_rate,
        artist_name=tags.get('artist', '').strip(),
        album_name=tags.get('album', '').strip(),
        genre_name=tags.get('genre', '').strip(),
        lyrics=tags.get('lyrics', '').strip(),
        notes=tags.get('notes', '').strip(),
        track_number=track_number,
        file_path=file_path,
        file_size=file_size,
        file_managed=copy,
        file_type=meta.mime[0],
    )
    # If the album doesn't have any artwork yet, try to pull it out of the tags.
    if track.album and not track.album.artwork_path:
        try:
            path = os.path.join(track.artist_name, track.album_name, 'artwork.tmp')
            track.album.artwork_type, data = extract_artwork(meta.tags)
            track.album.artwork_path = library_storage.save(path, ContentFile(data))
            track.album.save()
        except:
            pass
    return track

def scan_directory(dir_path, owner=None):
    if owner is None:
        owner = User.objects.get()
    for root, dirs, files in os.walk(dir_path):
        for name in files:
            _base, ext = os.path.splitext(name)
            if ext[1:].lower() in settings.JUQUE_SCAN_EXTENSIONS:
                file_path = os.path.abspath(os.path.join(root, name))
                try:
                    track = create_track(file_path, owner)
                    logger.info('Added track: %s', track)
                except:
                    logger.exception('Error adding: %s', file_path)

class RangeFileWrapper (object):
    def __init__(self, filelike, blksize=8192, offset=0, length=None):
        self.filelike = filelike
        self.filelike.seek(offset, os.SEEK_SET)
        self.remaining = length
        self.blksize = blksize

    def close(self):
        if hasattr(self.filelike, 'close'):
            self.filelike.close()

    def __iter__(self):
        return self

    def next(self):
        if self.remaining is None:
            # If remaining is None, we're reading the entire file.
            data = self.filelike.read(self.blksize)
            if data:
                return data
            raise StopIteration()
        else:
            if self.remaining <= 0:
                raise StopIteration()
            data = self.filelike.read(min(self.remaining, self.blksize))
            if not data:
                raise StopIteration()
            self.remaining -= len(data)
            return data

def render_thumbnail(album):
    cache_key = 'thumbnail-%s' % album.artwork_path
    data = cache.get(cache_key)
    if data:
        return data
    im = Image.open(library_storage.path(album.artwork_path))
    thumb = Image.new('RGB', (640, 640))
    w, h = im.size
    if w >= h:
        ratio = 640.0 / w
        new_h = int(h * ratio)
        im = im.resize((640, new_h), Image.ANTIALIAS)
        thumb.paste(im, (0, (640 - new_h) / 2))
    else:
        ratio = 640.0 / h
        new_w = int(w * ratio)
        im = im.resize((new_w, 640), Image.ANTIALIAS)
        thumb.paste(im, ((640 - new_w) / 2, 0))
    data = StringIO()
    thumb.save(data, 'png')
    data.seek(0)
    data = data.getvalue()
    cache.set(cache_key, data, 60 * 60 * 24 * 7)
    return data

def get_query_html(obj, q=None):
    template_name = 'ajax/%s/query.html' % obj.__class__.__name__.lower()
    return loader.render_to_string(template_name, {'object': obj, 'query': q})
