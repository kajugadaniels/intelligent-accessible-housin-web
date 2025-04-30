from users.views import *
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

app_name = 'users'

urlpatterns = [
    path('dashboard/', dashboard, name="dashboard"),
    path('search/', search, name="search"),

    path('properties/', properties, name="properties"),

    path('notifications/', notifications, name="notifications"),
]  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)