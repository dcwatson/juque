from django.conf import settings
from django.core.cache import cache, CacheKeyWarning
import requests
import hashlib
import time

def cache_key(params):
    parts = []
    for key in sorted(params):
        parts.append('%s=%s' % (key, params[key]))
    return hashlib.md5(';'.join(parts)).hexdigest()

def api_call(params):
    key = cache_key(params)
    info = cache.get(key)
    if info is None:
        last_call = cache.get('lastfm_last_call_time')
        call_time = 1.0 / settings.LASTFM_CALLS_PER_SECOND
        if last_call:
            since = time.time() - last_call
            if since < call_time:
                time.sleep(call_time - since)
        cache.set('lastfm_last_call_time', time.time(), 30)
        r = requests.get(settings.LASTFM_ENDPOINT, params=params)
        info = r.json()
        cache.set(key, info, settings.LASTFM_CACHE_TIME)
    return info

def get_album_info(artist_name, album_name):
    return api_call({
        'api_key': settings.LASTFM_API_KEY,
        'method': 'album.getinfo',
        'artist': artist_name,
        'album': album_name,
        'autocorrect': '1',
        'format': 'json',
    })['album']

def get_album_artwork(artist_name, album_name):
    info = get_album_info(artist_name, album_name)
    images = {}
    for i in info['image']:
        images[i['size']] = i['#text']
    # Try getting the largest image possible, and work backwards from there.
    for s in ('mega', 'extralarge', 'large', 'medium', 'small'):
        try:
            r = requests.get(images[s])
            mime = r.headers['Content-Type'].split(';')[0]
            return mime, r.content
        except:
            pass

def get_track_info(artist_name, track_name):
    return api_call({
        'api_key': settings.LASTFM_API_KEY,
        'method': 'track.getinfo',
        'artist': artist_name,
        'track': track_name,
        'autocorrect': '1',
        'format': 'json',
    })['track']
