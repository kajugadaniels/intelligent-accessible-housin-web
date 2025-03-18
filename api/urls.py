from api.views import *
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

app_name = 'api'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('properties/', GetPropertiesView.as_view(), name='getProperties'),
    path('property/<int:id>/', ShowPropertyView.as_view(), name='showProperty'),
]  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)