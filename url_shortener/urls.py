from django.urls import path
from .views import URLListCreateAPIView, URLStatsAPIView

urlpatterns = [
    path('shorten/', URLListCreateAPIView.as_view(), name='url-list-create'),
    path('stats/<str:short_code>/', URLStatsAPIView.as_view(), name='stats'),
]
