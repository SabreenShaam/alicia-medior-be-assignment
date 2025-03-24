from django.contrib.auth.models import User
from django.db import models
import hashlib
import base64
import string
import random
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from url_shortener.exceptions import URLValidationError, ShortCodeExistsError


class URL(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='urls', null=True, blank=True)
    long_url = models.URLField(max_length=2000)
    short_code = models.CharField(max_length=15, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    access_count = models.PositiveIntegerField(default=0)
    is_private = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.short_code} -> {self.long_url}"

    @classmethod
    def create_short_url(cls, long_url, user=None, custom_code=None, is_private=False):
        validate = URLValidator()
        try:
            validate(long_url)
        except ValidationError:
            raise URLValidationError()

        if user:
            existing_url = cls.objects.filter(long_url=long_url, user=user).first()
            if existing_url:
                return existing_url
        else:
            existing_url = cls.objects.filter(long_url=long_url, is_private=False, user=None).first()
            if existing_url:
                return existing_url

        if custom_code:
            if cls.objects.filter(short_code=custom_code).exists():
                raise ShortCodeExistsError()
            short_code = custom_code
        else:
            short_code = cls.generate_short_code()
            while cls.objects.filter(short_code=short_code).exists():
                short_code = cls.generate_short_code()

        return cls.objects.create(
            long_url=long_url,
            short_code=short_code,
            user=user,
            is_private=is_private
        )

    @staticmethod
    def generate_short_code(length=6):
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
