from django.conf import settings
from django.core.files.base import File, ContentFile
from django.core.files.storage import FileSystemStorage
from django.utils.text import slugify as django_slugify
from juque.core.models import User
from juque.lastfm import get_album_info, get_album_artwork, get_track_info
from mutagen import id3, mp4, File as scan_file
import mimetypes
import datetime
import logging
import os

logger = logging.getLogger(__name__)

library_storage = FileSystemStorage(location=settings.MEDIA_ROOT, base_url=settings.MEDIA_URL)

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
        'trkn': 'track',
    }
}

def slugify(name, strip_words=False, strip_parens=True):
    name = name.lower()
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

def update_album(album, update_artist=True, update_tracks=True, update_artwork=True):
    info = get_album_info(album.artist.name, album.name)
    if update_artist:
        album.artist.name = info['artist'].strip()
        album.artist.musicbrainz_id = info['tracks']['track'][0]['artist']['mbid']
        album.artist.save()
    if update_tracks:
        for t in info['tracks']['track']:
            match = slugify(t['name'], strip_words=True)
            try:
                track = album.tracks.get(match_name=match)
                track.name = t['name'].strip()
                track.track_number = int(t['@attr']['rank'])
                track.musicbrainz_id = t['mbid'].strip()
                track.save()
            except Track.DoesNotExist:
                pass
    album.name = info['name'].strip()
    album.musicbrainz_id = info['mbid'].strip()
    album.num_tracks = len(info['tracks']['track'])
    try:
        s = info['releasedate'].strip().split(',')[0]
        album.release_date = datetime.datetime.strptime(s, '%d %b %Y').date()
    except:
        pass
    if update_artwork:
        try:
            mime, data = get_album_artwork(album)
            ext = mimetypes.guess_extension(mime)
            # What a ridiculous default extension for image/jpeg.
            if ext == '.jpe':
                ext = '.jpg'
            path = 'album-art/%s%s' % (album.pk, ext)
            if library_storage.exists(path):
                library_storage.delete(path)
            album.artwork_path = library_storage.save(path, ContentFile(data))
        except:
            pass
    album.save()

def update_track(track, update_artist=True):
    info = get_track_info(track.artist.name, track.name)
    if update_artist:
        track.artist.name = info['artist']['name'].strip()
        track.artist.musicbrainz_id = info['artist']['mbid'].strip()
        track.artist.save()
    track.name = info['name'].strip()
    track.musicbrainz_id = info['mbid'].strip()
    track.save()

def create_track(file_path, owner, copy=None):
    from juque.library.models import Track, Artist, Album, Genre, library_storage
    if copy is None:
        copy = settings.JUQUE_COPY_SOURCE
    file_size = os.path.getsize(file_path)
    meta = scan_file(file_path)
    if not meta or not meta.tags:
        logger.warning('No tags found in %s; Skipping.', file_path)
        return
    tags = map_tags(meta.tags)
    try:
        title = tags['title']
    except:
        title = os.path.basename(file_path)
    artist = None
    album = None
    genre = None
    track = 0
    if 'artist' in tags:
        artist_name = tags['artist']
        try:
            artist = Artist.objects.get(slug=slugify(artist_name))
        except:
            artist = Artist.objects.create(name=artist_name)
    if 'album' in tags:
        album_name = tags['album']
        try:
            # Make sure we don't grab a "bare" album (without an artist), since they are essentially
            # one-offs for tracks not specifying an artist. Just because the names may match, doesn't mean
            # the tracks are off the same album unless the artist matches too.
            album = Album.objects.get(artist=artist, artist__isnull=False, slug=slugify(album_name))
        except:
            album = Album.objects.create(name=album_name, artist=artist)
    if 'genre' in tags:
        genre_name = tags['genre']
        try:
            genre = Genre.objects.get(slug=slugify(genre_name))
        except:
            genre = Genre.objects.create(name=genre_name)
    if 'track' in tags:
        if tags['track'].isdigit():
            track = int(tags['track'])
        elif '/' in tags['track']:
            try:
                track = int(tags['track'].split('/')[0])
            except:
                pass
    t = Track.objects.create(
        owner=owner,
        name=title,
        length=meta.info.length,
        bitrate=meta.info.bitrate,
        sample_rate=meta.info.sample_rate,
        artist=artist,
        album=album,
        genre=genre,
        track_number=track,
        file_path=file_path,
        file_size=file_size,
        file_managed=copy,
        file_type=meta.mime[0],
    )
    if copy:
        ext = mimetypes.guess_extension(t.file_type)
        new_path = 'tracks/%s%s' % (t.pk, ext)
        with open(file_path, 'rb') as f:
            t.file_path = library_storage.save(new_path, File(f))
        t.save()
    return t

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
