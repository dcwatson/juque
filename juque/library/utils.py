from django.conf import settings
from juque.library.models import Track, Artist, Album, Genre
from mutagen import id3, mp4, File as scan_file
import subprocess
import datetime
import random
import shutil
import pytz
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

HEX_CHARS = '0123456789ABCDEF'

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

def process_track(file_path, track):
    file_name = os.path.basename(file_path)
    _base, ext = os.path.splitext(file_name)
    new_path = os.path.join(track.media_root, 'source%s' % ext)
    if not os.path.exists(track.media_root):
        # If the track media directory doesn't exist, create it and copy the source file into it.
        os.makedirs(track.media_root)
        # Copy the source file into the track's media root.
        print 'Copying %s to %s' % (file_name, track.media_root)
        shutil.copy(file_path, new_path)
    args = [
        settings.JUQUE_FFMPEG_BINARY,
        '-i', new_path,
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
    subprocess.call(args, cwd=track.media_root)
    for name in os.listdir(track.media_root):
        if not name.endswith('.ts'):
            continue
        args = [
            settings.JUQUE_OPENSSL_BINARY,
            'aes-128-cbc',
            '-e',
            '-in', name,
            '-out', name + '.aes',
            '-nosalt',
            '-K', track.aes_key,
            '-iv', track.aes_iv,
        ]
        print '  Encrypting %s -> %s.aes' % (name, name)
        subprocess.call(args, cwd=track.media_root)
        # Remove the unencrypted file, rename the encrypted file.
        old_path = os.path.join(track.media_root, name)
        new_path = os.path.join(track.media_root, name + '.aes')
        os.unlink(old_path)
        os.rename(new_path, old_path)

def create_track(file_path):
    meta = scan_file(file_path)
    tags = map_tags(meta.tags)
    if 'title' not in tags:
        raise Exception('No title for: %s' % file_path)
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
    aes_key = ''.join([random.choice(HEX_CHARS) for i in range(32)])
    aes_iv = ''.join([random.choice(HEX_CHARS) for i in range(32)])
    return Track.objects.create(
        name=tags['title'],
        length=meta.info.length,
        bitrate=meta.info.bitrate,
        sample_rate=meta.info.sample_rate,
        artist=artist,
        album=album,
        genre=genre,
        aes_key=aes_key,
        aes_iv=aes_iv,
    )

def scan_directory(dir_path):
    local_tz = pytz.timezone(settings.TIME_ZONE)
    for root, dirs, files in os.walk(dir_path):
        for name in files:
            _base, ext = os.path.splitext(name)
            if ext[1:].lower() in settings.JUQUE_SCAN_FILETYPES:
                file_path = os.path.join(root, name)
                track = create_track(file_path)
                process_track(file_path, track)
