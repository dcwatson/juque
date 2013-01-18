from django.shortcuts import get_object_or_404, render
from django.conf import settings
from django.http import HttpResponse
from juque.library.models import Track
from juque.library.utils import aes_pad
from Crypto.Cipher import AES
import subprocess
import mimetypes
import binascii

def track_play(request, track_id):
    track = get_object_or_404(Track, pk=track_id)
    return render(request, 'player/play.html', {
        'track': track,
    })

def track_stream(request, track_id):
    track = get_object_or_404(Track, pk=track_id)
    r = request.META.get('HTTP_RANGE')
    ct, encoding = mimetypes.guess_type(track.file_path)
    with open(track.file_path, 'rb') as fp:
        data = fp.read()
    hdr = None
    status = 200
    if r and r.startswith('bytes='):
        start, end = r[6:].split('-', 1)
        start = int(start) if start else 0
        end = int(end) if end else len(data) - 1
        if end >= len(data):
            end = len(data) - 1
        hdr = 'bytes %s-%s/%s' % (start, end, len(data))
        print hdr
        data = data[start:end]
        status = 206 if data else 204 # Partial content (206) or No content (204)
    resp = HttpResponse(data, status=status, content_type=ct)
    resp['Accept-Ranges'] = 'bytes'
    if hdr:
        resp['Content-Range'] = hdr
    return resp

class Transcoder (object):
    def __init__(self, track, codec, bitrate='128k', buffer_size=8192):
        args = [
            settings.JUQUE_FFMPEG_BINARY,
            '-v', 'quiet',
            '-i', track.file_path,
            '-acodec', codec,
            '-ab', bitrate,
            '-f', 'mpegts',
            '-',
        ]
        self.buffer_size = buffer_size
        self.process = subprocess.Popen(args, stdout=subprocess.PIPE)
    def close(self):
        if self.process.returncode is not None:
            return
        self.process.stdout.close()
        try:
            self.process.terminate()
        except:
            pass
        self.process.wait()
    def __iter__(self):
        while True:
            try:
                data = self.process.stdout.read(self.buffer_size)
                if not data:
                    break
                yield '%s\r\n%s\r\n' % (hex(len(data))[2:], data)
            except GeneratorExit:
                print 'GENERATOR EXIT'
                break
            except:
                break
        self.close()
        yield '0\r\n'
    def __del__(self):
        self.close()

def track_transcode(request, track_id, codec):
    try:
        from wsgiref import util
        util._hoppish = {}.__contains__
    except:
        pass
    track = get_object_or_404(Track, pk=track_id)
    ct, encoding = mimetypes.guess_type('filename.%s' % codec)
    resp = HttpResponse(ChunkedTranscoder(track, codec), content_type=ct)
    resp['Transfer-Encoding'] = 'chunked'
    return resp
