from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import redirect, get_object_or_404

from .exceptions import RateLimitExceededError, ShortCodeNotFoundError
from .models import URL
from .serializers import URLSerializer
from django.http import Http404
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class CustomRateThrottle(AnonRateThrottle):
    def throttled(self, request, wait):
        raise RateLimitExceededError(detail=f"Rate limit exceeded. Try again in {wait} seconds.")


class URLListCreateAPIView(APIView):
    throttle_classes = [CustomRateThrottle, UserRateThrottle]

    def get(self, request):
        urls = URL.objects.all()
        serializer = URLSerializer(urls, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        serializer = URLSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class URLDetailAPIView(APIView):
    throttle_classes = [CustomRateThrottle, UserRateThrottle]

    def get_object(self, short_code):
        try:
            return get_object_or_404(URL, short_code=short_code)
        except Http404:
            raise ShortCodeNotFoundError()

    def get(self, request, short_code):
        url_obj = self.get_object(short_code)
        serializer = URLSerializer(url_obj, context={'request': request})
        return Response(serializer.data)


class URLRedirectAPIView(APIView):
    throttle_classes = [CustomRateThrottle, UserRateThrottle]

    def get(self, request, short_code):
        try:
            url_obj = get_object_or_404(URL, short_code=short_code)
            url_obj.access_count += 1
            url_obj.save()
            return redirect(url_obj.long_url)
        except Http404:
            raise ShortCodeNotFoundError()


class URLStatsAPIView(APIView):
    throttle_classes = [CustomRateThrottle, UserRateThrottle]

    def get(self, request, short_code):
        try:
            url_obj = get_object_or_404(URL, short_code=short_code)
            serializer = URLSerializer(url_obj, context={'request': request})
            return Response(serializer.data)
        except Http404:
            raise ShortCodeNotFoundError()
