import random
import string
from django.db import models


def generate_short_url():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))


class ShortenedUrl(models.Model):
    original_url = models.URLField(max_length=2048)
    short_code = models.CharField(max_length=10, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    access_count = models.PositiveIntegerField(default=0)
    last_accessed = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.short_code:
            self.short_code = generate_short_url()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.short_code} -> {self.original_url}"
