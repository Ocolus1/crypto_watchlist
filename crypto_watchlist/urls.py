# crypto_watchlist/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('watchlist.urls')),  # Include your app's URLs
]
