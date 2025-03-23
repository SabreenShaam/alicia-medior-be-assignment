from rest_framework import serializers
from .models import URL


class URLSerializer(serializers.ModelSerializer):
    short_url = serializers.SerializerMethodField()
    custom_code = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = URL
        fields = ['long_url', 'short_url', 'created_at', 'access_count', 'custom_code']
        read_only_fields = ['short_url', 'created_at', 'access_count']

    def get_short_url(self, obj):
        request = self.context.get('request')
        domain = request.build_absolute_uri('/')[:-1]
        return f"{domain}/short/{obj.short_code}"

    def create(self, validated_data):
        long_url = validated_data.get('long_url')
        custom_code = validated_data.get('custom_code', None)

        url_obj = URL.create_short_url(long_url, custom_code)
        return url_obj
