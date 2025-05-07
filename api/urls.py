from api.views import *
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

app_name = 'api'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('verify_token/', VerifyTokenView.as_view(), name='verify_token'),

    path('dashboard/', DashboardAPIView.as_view(), name='dashboard'),

    path('amenities/', GetAmenitiesView.as_view(), name='getAmenities'),
    path('amenity/<int:id>/', ShowAmenityView.as_view(), name='showAmenity'),

    path('categories/', GetCategoriesView.as_view(), name='getCategories'),
    path('category/<int:id>/', ShowCategoryView.as_view(), name='showCategory'),

    path('properties/', GetPropertiesView.as_view(), name='getProperties'),
    path('property/<int:id>/', ShowPropertyView.as_view(), name='showProperty'),

    path('notifications/',  NotificationsAPIView.as_view(), name='notifications'),

    path('applications/', ApplicationsAPIView.as_view(), name='applications'),
]  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)