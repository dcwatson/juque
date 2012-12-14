from django.conf import settings
from django.core.files.base import File, ContentFile
from juque.library.models import Track, Artist, Album, Genre, get_match_name
from juque.core.models import User
from mutagen import id3, mp4, File as scan_file
from Crypto.Cipher import AES
import subprocess
import binascii
import datetime
import tempfile
import hashlib
import shutil
import csv
import os

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
        'aART':    'albumartist',
        '\xa9grp': 'grouping',
        '\xa9day': 'date',
        '\xa9gen': 'genre',
        '\xa9lyr': 'lyrics',
        'trkn': 'track',
    }
}

def map_tags(tags):
    mapper = TAG_MAPPERS[tags.__class__]
    mapped_tags = {}
    for key, value in tags.items():
        if isinstance(value, (list, tuple)):
            value = value[0]
        if key in mapper:
            mapped_tags[mapper[key]] = unicode(value).strip().replace('\x00', '')
    return mapped_tags

def aes_pad(text, block_size, zero=False):
    num = block_size - (len(text) % block_size)
    ch = '\0' if zero else chr(num)
    return text + (ch * num)

def segment_track(track):
    storage = track.owner.get_storage()
    temp_dir = tempfile.mkdtemp(suffix='.juque')
    args = [
        settings.JUQUE_FFMPEG_BINARY,
        '-i', storage.path(track.file_path),
        '-acodec', settings.JUQUE_SEGMENT_CODEC,
        '-ab', settings.JUQUE_SEGMENT_BITRATE,
        '-map', '0:0',
        '-f', 'segment',
        '-segment_list', 'segments.csv',
        '-segment_time', str(settings.JUQUE_SEGMENT_SIZE),
        '-segment_format', 'mpegts',
        '-v', 'quiet',
        '%04d.ts',
    ]
    subprocess.call(args, cwd=temp_dir)
    # Generate a random key and IV to encrypt the segments.
    key = os.urandom(16)
    iv = os.urandom(16)
    # Store the key and IV encoded as hex.
    track.segment_aes_key = binascii.hexlify(key)
    track.segment_aes_iv = binascii.hexlify(iv)
    # Encrypt each segment, and save it using the appropriate storage.
    cipher = AES.new(key, AES.MODE_CBC, iv)
    seg_file = os.path.join(temp_dir, 'segments.csv')
    with open(seg_file, 'rb') as sf:
        for row in csv.reader(sf):
            seg_path = 'segments/%s/%s/%s/%s' % (track.file_hash[0], track.file_hash[1], track.file_hash, row[0])
            with open(os.path.join(temp_dir, row[0]), 'rb') as f:
                data = cipher.encrypt(aes_pad(f.read(), cipher.block_size))
                seg_path = storage.save(seg_path, ContentFile(data))
                track.segments.create(start_time=float(row[1]), end_time=float(row[2]), file_path=seg_path)
    track.save()
    shutil.rmtree(temp_dir)

def create_track(file_path, owner, copy=None):
    if copy is None:
        copy = settings.JUQUE_COPY_SOURCE
    with open(file_path, 'rb') as f:
        data = f.read()
        file_size = len(data)
        file_hash = hashlib.md5(data).hexdigest()
    try:
        return Track.objects.get(file_hash=file_hash)
    except:
        pass
    meta = scan_file(file_path)
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
        artist_match = get_match_name(artist_name)
        try:
            artist = Artist.objects.get(match_name=artist_match)
        except:
            artist = Artist.objects.create(name=artist_name, match_name=artist_match)
    if 'album' in tags:
        album_name = tags['album']
        album_match = get_match_name(album_name)
        try:
            # Make sure we don't grab a "bare" album (without an artist), since they are essentially
            # one-offs for tracks not specifying an artist. Just because the names may match, doesn't mean
            # the tracks are off the same album unless the artist matches too.
            album = Album.objects.get(artist=artist, artist__isnull=False, match_name=album_match)
        except:
            album = Album.objects.create(name=album_name, artist=artist, match_name=album_match)
    if 'genre' in tags:
        genre_name = tags['genre']
        genre_match = get_match_name(genre_name)
        try:
            genre = Genre.objects.get(match_name=genre_match)
        except:
            genre = Genre.objects.create(name=genre_name, match_name=genre_match)
    if 'track' in tags and tags['track'].isdigit():
        track = int(tags['track'])
    if copy:
        storage = owner.get_storage()
        ext = file_path.split('.')[-1].lower()
        new_path = 'tracks/%s/%s/%s.%s' % (file_hash[0], file_hash[1], file_hash, ext)
        with open(file_path, 'rb') as f:
            file_path = storage.save(new_path, File(f))
    return Track.objects.create(
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
        file_hash=file_hash,
    )

def scan_directory(dir_path, owner=None):
    if owner is None:
        owner = User.objects.get()
    for root, dirs, files in os.walk(dir_path):
        for name in files:
            _base, ext = os.path.splitext(name)
            if ext[1:].lower() in settings.JUQUE_SCAN_EXTENSIONS:
                file_path = os.path.abspath(os.path.join(root, name))
                track = create_track(file_path, owner)
                if settings.JUQUE_SEGMENT:
                    segment_track(track)
