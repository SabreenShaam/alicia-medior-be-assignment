from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import redirect, get_object_or_404

from .exceptions import RateLimitExceededError, ShortCodeNotFoundError, UnauthorisedError, ForbiddenError
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
        if request.user.is_authenticated:
            if request.user.is_superuser:
                urls = URL.objects.all()
            else:
                public_urls = URL.objects.filter(is_private=False).exclude(user=request.user)
                user_urls = URL.objects.filter(user=request.user)
                urls = public_urls.union(user_urls)

        else:
            urls = URL.objects.filter(is_private=False)

        serializer = URLSerializer(urls, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        serializer = URLSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class URLRedirectAPIView(APIView):
    throttle_classes = [CustomRateThrottle, UserRateThrottle]

    def get(self, request, short_code):
        try:
            url_obj = get_object_or_404(URL, short_code=short_code)
            if url_obj.is_private:
                if url_obj.user != request.user and not request.user.is_superuser:
                    raise ForbiddenError()

            url_obj.access_count += 1
            url_obj.save()
            return redirect(url_obj.long_url, permanent=True)
        except Http404:
            raise ShortCodeNotFoundError()


class URLStatsAPIView(APIView):
    throttle_classes = [CustomRateThrottle, UserRateThrottle]

    def get(self, request, short_code):
        try:
            url_obj = get_object_or_404(URL, short_code=short_code)
            if url_obj.is_private:
                if url_obj.user != request.user and not request.user.is_superuser:
                    raise ForbiddenError()
            serializer = URLSerializer(url_obj, context={'request': request})
            return Response(serializer.data)
        except Http404:
            raise ShortCodeNotFoundError()
