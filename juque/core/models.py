from django.db import models
from django.conf import settings
from django.core.files.storage import get_storage_class
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.translation import ugettext_lazy as _
from juque.core.utils import EncryptedTextField

STORAGE_CHOICES = (
    ('django.core.files.storage.FileSystemStorage', 'Local'),
    ('storages.backends.s3boto.S3BotoStorage', 'Amazon S3'),
)

class UserManager (BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(name=name.strip(), email=UserManager.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password, **extra_fields):
        _admin = extra_fields.pop('is_admin', True)
        return self.create_user(email, name, password=password, is_admin=True, **extra_fields)

class User (AbstractBaseUser):
    name = models.CharField(max_length=200)
    email = models.EmailField(_('email address'), unique=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    storage_backend = models.CharField(max_length=100, choices=STORAGE_CHOICES, default='django.core.files.storage.FileSystemStorage')
    aws_bucket = models.CharField(max_length=100, blank=True)
    aws_access_key = EncryptedTextField(blank=True)
    aws_secret_key = EncryptedTextField(blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('name',)

    objects = UserManager()

    def __unicode__(self):
        return self.name

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

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
