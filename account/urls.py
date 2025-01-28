from account.views import *
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

app_name = 'auth'

urlpatterns = [
    path('', user_login, name="login"),
    path('logout/', user_logout, name='logout'),

    path('profile/', editProfile, name='editProfile'),
]  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)