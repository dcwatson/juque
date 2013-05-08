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

# Build artwork storage backend.
artwork_storage_cls = get_storage_class(settings.JUQUE_STORAGES['artwork']['backend'])
artwork_storage = artwork_storage_cls(**settings.JUQUE_STORAGES['artwork']['options'])

# Build library storage backend.
library_storage_cls = get_storage_class(settings.JUQUE_STORAGES['library']['backend'])
library_storage = library_storage_cls(**settings.JUQUE_STORAGES['library']['options'])

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

def update_track(track, autocorrect=True, update_artist=True, update_album=True):
    info = get_track_info(track.artist_name, track.name, autocorrect=autocorrect)
    if autocorrect:
        if 'artist' in info and 'name' in info['artist']:
            track.artist_name = info['artist']['name'].strip()
        if 'album' in info and 'title' in info['album']:
            track.album_name = info['album']['title'].strip()
        if 'name' in info:
            track.name = info['name'].strip()
    if 'mbid' in info:
        track.musicbrainz_id = info['mbid'].strip()
    if 'album' in info and '@attr' in info['album'] and 'position' in info['album']['@attr']:
        try:
            track.track_number = int(info['album']['@attr']['position'])
        except:
            pass
    # We need to call save() so the related Artist and Album objects are created/updated as needed.
    track.save()
    if update_artist and 'artist' in info and 'mbid' in info['artist']:
        track.artist.musicbrainz_id = info['artist']['mbid'].strip()
        track.artist.save()
    if update_album and 'album' in info:
        if 'mbid' in info['album']:
            track.album.musicbrainz_id = info['album']['mbid'].strip()
        if not track.album.artwork_path and 'image' in info['album']:
            image_urls = {}
            for i in info['album']['image']:
                image_urls[i['size']] = i['#text']
            # Try to get the largest album artwork we can.
            for s in ('mega', 'extralarge', 'large', 'medium', 'small'):
                try:
                    r = requests.get(image_urls[s])
                    mime = r.headers['Content-Type'].split(';')[0]
                    logger.debug('Downloaded %s for %s', image_urls[s], track.album_name)
                    ext = mimetypes.guess_extension(mime)
                    # What a ridiculous default extension for image/jpeg.
                    if ext == '.jpe':
                        ext = '.jpg'
                    path = 'album-art/%s%s' % (track.album.pk, ext)
                    if artwork_storage.exists(path):
                        artwork_storage.delete(path)
                        logger.debug('Deleted existing artwork at %s', path)
                    track.album.artwork_path = artwork_storage.save(path, ContentFile(r.content))
                    break
                except:
                    pass
        track.album.save()

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
    if copy:
        ext = os.path.splitext(track.file_path)[1]
        new_path = 'tracks/%s%s' % (track.pk, ext)
        with open(file_path, 'rb') as f:
            track.file_path = library_storage.save(new_path, File(f))
        track.save()
    if settings.LASTFM_ENABLE and track.artist:
        update_track(track)
    return track

def scan_directory(dir_path, owner=None):
    if owner is None:
        owner = User.objects.get()
    for root, dirs, files in os.walk(dir_path):
        for name in files:
            _base, ext = os.path.splitext(name)
            if ext[1:].lower() in settings.JUQUE_SCAN_EXTENSIONS:
                file_path = os.path.abspath(os.path.join(root, name))
                track = create_track(file_path, owner)
                logger.info('Added track: %s', track)

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
    im = Image.open(artwork_storage.path(album.artwork_path))
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
