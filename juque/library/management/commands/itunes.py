from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils.dateparse import parse_datetime
from juque.library.models import Artist, Album, Genre, Track
from juque.library.utils import slugify
import plistlib
import logging
import pytz

logger = logging.getLogger(__name__)

class Command (BaseCommand):
    def handle(self, *args, **options):
        pl = plistlib.readPlist(args[0])
        updated = 0
        tz = pytz.timezone(settings.TIME_ZONE)
        for track_id, info in pl['Tracks'].items():
            name_match = slugify(info['Name'], strip_words=True)
            artist_match = slugify(info['Artist'], strip_words=True)
            track = None
            try:
                album_match = slugify(info['Album'], strip_words=True)
                track = Track.objects.get(match_name=name_match, artist__match_name=artist_match, album__match_name=album_match)
            except:
                try:
                    track = Track.objects.get(match_name=name_match, artist__match_name=artist_match)
                except:
                    pass
            if track:
                track.play_count = info.get('Play Count', track.play_count)
                track.date_added = info.get('Date Added', track.date_added)
                track.save()
                logger.info('Updated %s, play count = %s, date added = %s', track, track.play_count, track.date_added)
                updated += 1
        print '%s tracks updated.' % updated
