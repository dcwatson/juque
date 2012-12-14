from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from juque.library.utils import scan_directory

class Command (BaseCommand):
    args = '<path> <path> ...'

    def handle(self, *args, **options):
        for root in args:
            print 'Scanning %s' % root
            scan_directory(root)
