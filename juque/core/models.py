from django.db import models
from django.conf import settings
from django.core.files.storage import get_storage_class
from juque.core.utils import EncryptedTextField

STORAGE_CHOICES = (
    ('django.core.files.storage.FileSystemStorage', 'Local'),
    ('storages.backends.s3boto.S3BotoStorage', 'Amazon S3'),
)

class User (models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=200)
    storage_backend = models.CharField(max_length=100, choices=STORAGE_CHOICES)
    aws_bucket = models.CharField(max_length=100, blank=True)
    aws_access_key = EncryptedTextField(blank=True)
    aws_secret_key = EncryptedTextField(blank=True)

    def __unicode__(self):
        return self.name

    def get_storage(self):
        cls = get_storage_class(self.storage_backend)
        params = {
            'django.core.files.storage.FileSystemStorage': {
                'location': settings.MEDIA_ROOT,
                'base_url': settings.MEDIA_URL,
            },
            'storages.backends.s3boto.S3BotoStorage': {
                'bucket': self.aws_bucket,
                'access_key': self.aws_access_key,
                'secret_key': self.aws_secret_key,
                'secure_urls': False,
            }
        }.get(self.storage_backend, {})
        return cls(**params)
