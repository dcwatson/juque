from django.conf import settings
from django.core.files.base import File, ContentFile
from juque.library.models import Track, Artist, Album, Genre
from juque.core.models import User
from mutagen import id3, mp4, File as scan_file
from Crypto.Cipher import AES
import subprocess
import binascii
import datetime
import tempfile
import random
import shutil
import pytz
import csv
import os
import re

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

def get_match_name(name):
    return re.sub(r'[^a-zA-Z0-9]+', '_', name).lower().strip('_')

def aes_pad(text, block_size, zero=False):
    num = block_size - (len(text) % block_size)
    ch = '\0' if zero else chr(num)
    return text + (ch * num)

def process_segments(temp_dir, track):
    key = binascii.unhexlify(track.aes_key)
    iv = binascii.unhexlify(track.aes_iv)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    seg_file = os.path.join(temp_dir, 'segments.csv')
    storage = track.owner.get_storage()
    print '   Processing segments...'
    with open(seg_file, 'rb') as sf:
        for row in csv.reader(sf):
            seg_path = 'tracks/%s/segments/%s' % (track.pk, row[0])
            with open(os.path.join(temp_dir, row[0]), 'rb') as f:
                data = cipher.encrypt(aes_pad(f.read(), cipher.block_size))
                seg_path = storage.save(seg_path, ContentFile(data))
                track.segments.create(start_time=float(row[1]), end_time=float(row[2]), file_path=seg_path)

def process_track(file_path, track):
    file_name = os.path.basename(file_path)
    temp_dir = tempfile.mkdtemp(suffix='.juque')
    print 'Created temp_dir', temp_dir
    _base, ext = os.path.splitext(file_name)
    track.file_path = 'tracks/%s/source%s' % (track.pk, ext)
    storage = track.owner.get_storage()
    with open(file_path, 'rb') as f:
        track.file_path = storage.save(track.file_path, File(f))
    # Now split the file into segments.
    args = [
        settings.JUQUE_FFMPEG_BINARY,
        '-i', file_path,
        '-acodec', 'mp3',
        '-ab', '128k',
        '-map', '0:0',
        '-f', 'segment',
        '-segment_list', 'segments.csv',
        '-segment_time', str(settings.JUQUE_SEGMENT_SIZE),
        '-segment_format', 'mpegts',
        '-v', 'quiet',
        '%04d.ts',
    ]
    print 'Encoding %s as 128k MP3 segments' % file_name
    subprocess.call(args, cwd=temp_dir)
    process_segments(temp_dir, track)
    track.save()
    shutil.rmtree(temp_dir)

def create_track(file_path, owner):
    meta = scan_file(file_path)
    tags = map_tags(meta.tags)
    try:
        title = tags['title']
    except:
        title = os.path.basename(file_path)
    artist = None
    album = None
    genre = None
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
    aes_key = binascii.hexlify(os.urandom(16))
    aes_iv = binascii.hexlify(os.urandom(16))
    return Track.objects.create(
        owner=owner,
        name=title,
        length=meta.info.length,
        bitrate=meta.info.bitrate,
        sample_rate=meta.info.sample_rate,
        artist=artist,
        album=album,
        genre=genre,
        aes_key=aes_key,
        aes_iv=aes_iv,
    )

def scan_directory(dir_path, owner=None):
    if owner is None:
        owner = User.objects.get()
    for root, dirs, files in os.walk(dir_path):
        for name in files:
            _base, ext = os.path.splitext(name)
            if ext[1:].lower() in settings.JUQUE_SCAN_FILETYPES:
                file_path = os.path.abspath(os.path.join(root, name))
                track = create_track(file_path, owner)
                process_track(file_path, track)
