from django.contrib import admin
from django.urls import include, path

from url_shortener.views.redirect_view import URLRedirectAPIView

urlpatterns = [
    path("admin/", admin.site.urls),
    path('short/<str:short_code>/', URLRedirectAPIView.as_view(), name='short-redirect'),
    path('api/', include('url_shortener.urls')),
]
