from django.shortcuts import get_object_or_404, render
from django.conf import settings
from django.http import HttpResponse
from juque.library.models import Track
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

class RecordingTranscoder (object):
    def __init__(self, track, codec, bitrate='64k', buffer_size=8192):
        args = [
            settings.JUQUE_FFMPEG_BINARY,
            '-v', 'quiet',
            '-i', track.file_path,
            '-acodec', codec,
            '-ab', bitrate,
            '-f', codec,
            '-',
        ]
        self.output_file = open('/Users/dcwatson/Desktop/transcode_output.mp3', 'wb')
        self.buffer_size = buffer_size
        self.process = subprocess.Popen(args, stdout=subprocess.PIPE)
    def close(self):
        print 'CLOSED'
        if self.process.returncode is not None:
            print self.process.returncode
            return
        self.process.stdout.close()
        self.process.terminate()
        self.process.wait()
        self.output_file.close()
    def __iter__(self):
        try:
            while True:
                data = self.process.stdout.read(self.buffer_size)
                if not data:
                    print 'FINISHED?'
                    break
                self.output_file.write(data)
                self.output_file.flush()
                yield data
        except GeneratorExit:
            print 'GENERATOR EXIT'
        self.close()
    def __del__(self):
        self.close()

def track_transcode(request, track_id, codec):
    track = get_object_or_404(Track, pk=track_id)
    ct, encoding = mimetypes.guess_type('filename.%s' % codec)
    return HttpResponse(RecordingTranscoder(track, codec), content_type=ct)
