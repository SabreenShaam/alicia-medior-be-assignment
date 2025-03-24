from django.urls import path
from url_shortener.views.create_view import URLListCreateAPIView
from url_shortener.views.stats_view import URLStatsAPIView

urlpatterns = [
    path('shorten/', URLListCreateAPIView.as_view(), name='url-list-create'),
    path('stats/<str:short_code>/', URLStatsAPIView.as_view(), name='stats'),
]
