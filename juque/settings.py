import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Dan Watson', 'dcwatson@gmail.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'juque.db'),
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(BASE_DIR, 'cache'),
    }
}

TIME_ZONE = 'America/New_York'
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

AUTH_USER_MODEL = 'core.User'
LOGIN_URL = '/login/'

USE_I18N = True
USE_L10N = True
USE_TZ = True

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(BASE_DIR, 'assets')
STATIC_URL = '/assets/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

SECRET_KEY = 'x)3e$lp92q=a)64id9ed)8mn3hxdhffp=u!f0&amp;^8h$q$mrzrkl'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'juque.urls'

WSGI_APPLICATION = 'juque.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'juque.core',
    'juque.library',
    'juque.playlists',
    'bootstrap',
    'compressor',
    'south',
    'tastypie',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'verbose': {
            'format': '%(name)s:%(lineno)d %(levelname)s %(asctime)s [pid: %(process)d] %(message)s',
        },
        'simple': {
            'format': '%(levelname)s %(message)s',
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'juque': {
            'level': 'DEBUG',
            'handlers': ['console'],
        }
    }
}

COMPRESS_ENABLED = True

JUQUE_SCAN_EXTENSIONS = ('mp3', 'm4a', 'mp4')
JUQUE_COPY_SOURCE = True
JUQUE_FFMPEG_BINARY = '/usr/bin/ffmpeg'

JUQUE_STORAGES = {
    'library': {
        'backend': 'storages.backends.s3boto.S3BotoStorage',
        'options': {
            'bucket': '',
            'access_key': '',
            'secret_key': '',
            'acl': 'private',
            'secure_urls': False,
        }
    },
    'artwork': {
        'backend': 'django.core.files.storage.FileSystemStorage',
        'options': {
            'location': MEDIA_ROOT,
            'base_url': MEDIA_URL,
        }
    }
}

LASTFM_ENABLE = False
LASTFM_ENDPOINT = 'http://ws.audioscrobbler.com/2.0/'
LASTFM_API_KEY = ''
LASTFM_CACHE_TIME = 60 * 60 * 24 * 14 # 2 week cache
LASTFM_CALLS_PER_SECOND = 2

try:
    _this_dir = os.path.abspath(os.path.dirname(__file__))
    execfile(os.path.join(_this_dir, 'local_settings.py'))
except:
    print '*** No local settings file found -- using defaults!'
