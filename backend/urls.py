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

    path('house-providers/', getHouseProviders, name="getHouseProviders"),
    path('house-provider/add/', addHouseProvider, name="addHouseProvider"),
    path('house-provider/<int:id>/', showHouseProvider, name="showHouseProvider"),
    path('house-provider/edit/<int:id>/', editHouseProvider, name="editHouseProvider"),
    path('house-provider/delete/<int:id>/', deleteHouseProvider, name="deleteHouseProvider"),

    path('amenities/', getAmenities, name="getAmenities"),
    path('amenity/add/', addAmenity, name="addAmenity"),
    path('amenity/<int:id>/', showAmenity, name="showAmenity"),
    path('amenity/edit/<int:id>/', editAmenity, name="editAmenity"),
    path('amenity/delete/<int:id>/', deleteAmenity, name="deleteAmenity"),

    path('properties/', getProperties, name="getProperties"),
    path('property/add/', addProperty, name="addProperty"),
    path('property/<int:id>/', showProperty, name="showProperty"),
    path('property/edit/<int:id>/', editProperty, name="editProperty"),
    path('property/delete/<int:id>/', deleteProperty, name="deleteProperty"),
    path('property/image/delete/<int:image_id>/', deletePropertyImage, name="deletePropertyImage"),

    path('rent-applications/', getRentApplications, name="getRentApplications"),
]  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)