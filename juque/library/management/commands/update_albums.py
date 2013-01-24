from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from juque.library.models import Album
from juque.library.utils import update_album
import logging

class Command (BaseCommand):
    def handle(self, *args, **options):
        for album in Album.objects.select_related('artist'):
            try:
                update_album(album)
            except Exception, ex:
                logging.exception('Error updating album: %s', album)
