from rest_framework import serializers
from .models import URL


class URLSerializer(serializers.ModelSerializer):
    short_url = serializers.SerializerMethodField()
    custom_code = serializers.CharField(write_only=True, required=False)
    is_private = serializers.BooleanField(required=False, default=False)
    username = serializers.SerializerMethodField()

    class Meta:
        model = URL
        fields = ['id', 'long_url', 'short_url', 'created_at', 'access_count',
                  'custom_code', 'is_private', 'username']
        read_only_fields = ['id', 'short_url', 'created_at', 'access_count', 'username']

    def get_short_url(self, obj):
        request = self.context.get('request')
        domain = request.build_absolute_uri('/')[:-1]
        return f"{domain}/short/{obj.short_code}"

    def get_username(self, obj):
        return obj.user.username if obj.user else "Anonymous"

    def create(self, validated_data):
        long_url = validated_data.get('long_url')
        custom_code = validated_data.get('custom_code', None)
        is_private = validated_data.get('is_private', False)

        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None

        if not user and is_private:
            raise serializers.ValidationError("Anonymous users cannot create private URLs")

        url_obj = URL.create_short_url(long_url, user, custom_code, is_private)
        return url_obj
