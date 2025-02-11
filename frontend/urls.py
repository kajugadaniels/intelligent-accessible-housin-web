from frontend.views import *
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

app_name = 'frontend'

urlpatterns = [
    path('login', userLogin, name="login"),
    path('register', userRegister, name="register"),

    path('', home, name="home"),
    path('properties', getProperties, name="getProperties"),
    path('property/<slug:slug>/', showProperty, name="showProperty"),
]  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)