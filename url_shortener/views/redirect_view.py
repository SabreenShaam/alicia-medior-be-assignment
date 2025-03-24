from rest_framework.views import APIView
from django.shortcuts import redirect, get_object_or_404
from django.http import Http404
from rest_framework.throttling import UserRateThrottle
from url_shortener.exceptions import ForbiddenError, ShortCodeNotFoundError
from url_shortener.models import URL
from url_shortener.utils import CustomRateThrottle


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
