from rest_framework import serializers
from url_shortener.models import URL


class StatsSerializer(serializers.ModelSerializer):
    short_url = serializers.SerializerMethodField()

    class Meta:
        model = URL
        fields = ["long_url", "short_url", "access_count"]

    def get_short_url(self, obj):
        request = self.context.get('request')
        domain = request.build_absolute_uri('/')[:-1]
        return f"{domain}/short/{obj.short_code}"
