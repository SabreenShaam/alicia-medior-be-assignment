from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import UserRateThrottle
from url_shortener.models import URL
from url_shortener.serializers.url_serializer import URLSerializer
from url_shortener.utils import CustomRateThrottle


class URLListCreateAPIView(APIView):
    throttle_classes = [CustomRateThrottle, UserRateThrottle]

    def get(self, request):
        if request.user.is_authenticated:
            if request.user.is_superuser:
                urls = URL.objects.all()
            else:
                urls = URL.objects.filter(
                    Q(is_private=False) | Q(user=request.user)
                ).select_related('user')

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
