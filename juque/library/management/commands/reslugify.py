from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from juque.library.models import Artist, Album, Genre, Track

class Command (BaseCommand):
    def handle(self, *args, **options):
        for model in (Artist, Album, Genre, Track):
            for obj in model.objects.all():
                obj.save()
