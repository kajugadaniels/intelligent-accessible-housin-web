from backend.views import *
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

app_name = 'backend'

urlpatterns = [
    path('', userLogin, name="login"),
    path('logout/', userLogout, name='logout'),
    path('profile/', userProfile, name='userProfile'),

    path('dashboard/', dashboard, name="dashboard"),

    path('amenities/', getAmenities, name="getAmenities"),
    path('amenity/add/', addAmenity, name="addAmenity"),
    path('amenity/<int:id>/', showAmenity, name="showAmenity"),
    path('amenity/edit/<int:id>/', editAmenity, name="editAmenity"),
    path('amenity/delete/<int:id>/', deleteAmenity, name="deleteAmenity"),
]  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)