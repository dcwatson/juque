from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import File
from juque.library.models import Track
from juque.library.utils import library_storage
import logging
import os

logger = logging.getLogger(__name__)

class Command (BaseCommand):
    def handle(self, *args, **options):
        for track in Track.objects.filter(file_managed=False):
            ext = os.path.splitext(track.file_path)[1]
            new_path = 'tracks/%s%s' % (track.pk, ext)
            with open(track.file_path, 'rb') as fp:
                track.file_path = library_storage.save(new_path, File(fp))
            track.file_managed = True
            track.save()
            logging.info('Uploaded "%s" to %s', track.name, track.file_path)
