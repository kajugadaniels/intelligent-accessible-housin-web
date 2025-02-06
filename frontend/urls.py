from frontend.views import *
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

app_name = 'frontend'

urlpatterns = [
    path('', home, name="home"),
    path('properties', getProperties, name="getProperties"),
    path('property/', showProperty, name="showProperty"),
]  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)