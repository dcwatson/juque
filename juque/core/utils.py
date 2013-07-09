from django.conf import settings
from django.db import models
from django.core.exceptions import ImproperlyConfigured
from Crypto.Cipher import AES
import base64

class EncryptedTextField (models.Field):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.prefix = kwargs.pop('prefix', '$aes-base64$')
        # TODO: key and/or keyfile args
        if len(settings.SECRET_KEY) < 32:
            raise ImproperlyConfigured('Your SECRET_KEY setting must be at least 32 characters long to use EncryptedTextField.')
        self.cipher = AES.new(settings.SECRET_KEY[:32])
        super(EncryptedTextField, self).__init__(*args, **kwargs)

    def is_encrypted(self, value):
        return isinstance(value, basestring) and value.startswith(self.prefix)

    def get_internal_type(self):
        return 'TextField'

    def to_python(self, value):
        if self.is_encrypted(value):
            value = self.cipher.decrypt(base64.b64decode(value[len(self.prefix):]))
            padding = ord(value[-1])
            if value[-padding:] != chr(padding) * padding:
                raise ValueError('Incorrect padding.')
            return value[:-padding]
        return value

    def get_prep_value(self, value):
        if value is not None and not self.is_encrypted(value):
            padding = self.cipher.block_size - (len(value) % self.cipher.block_size)
            value += chr(padding) * padding
            value = self.prefix + base64.b64encode(self.cipher.encrypt(value))
        return value
