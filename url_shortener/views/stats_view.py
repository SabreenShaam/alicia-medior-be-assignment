from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.http import Http404
from rest_framework.throttling import UserRateThrottle
from url_shortener.exceptions import ForbiddenError, ShortCodeNotFoundError
from url_shortener.models import URL
from url_shortener.serializers.stats_serializer import StatsSerializer
from url_shortener.utils import CustomRateThrottle


class URLStatsAPIView(APIView):
    throttle_classes = [CustomRateThrottle, UserRateThrottle]

    def get(self, request, short_code):
        try:
            url_obj = get_object_or_404(URL, short_code=short_code)
            if url_obj.is_private:
                if url_obj.user != request.user and not request.user.is_superuser:
                    raise ForbiddenError()
            serializer = StatsSerializer(url_obj, context={'request': request})
            return Response(serializer.data)
        except Http404:
            raise ShortCodeNotFoundError()
