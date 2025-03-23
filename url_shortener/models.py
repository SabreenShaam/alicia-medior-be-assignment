from django.db import models
import hashlib
import base64
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from url_shortener.exceptions import URLValidationError, ShortCodeExistsError


class URL(models.Model):
    long_url = models.URLField(max_length=2000)
    short_code = models.CharField(max_length=15, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    access_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.short_code} -> {self.long_url}"

    @classmethod
    def create_short_url(cls, long_url, custom_code=None):
        validate = URLValidator()
        try:
            validate(long_url)
        except ValidationError:
            raise URLValidationError()

        existing_url = cls.objects.filter(long_url=long_url).first()
        if existing_url:
            return existing_url

        if custom_code:
            if cls.objects.filter(short_code=custom_code).exists():
                raise ShortCodeExistsError()
            short_code = custom_code
        else:
            short_code = cls.generate_short_code(long_url)
            while cls.objects.filter(short_code=short_code).exists():
                short_code = cls.generate_short_code(long_url)

        return cls.objects.create(long_url=long_url, short_code=short_code)

    @staticmethod
    def generate_short_code(long_url, length=6):
        url_hash = hashlib.md5(long_url.encode()).digest()
        code = base64.urlsafe_b64encode(url_hash).decode('utf-8').replace('=', '')
        return code[:length]
