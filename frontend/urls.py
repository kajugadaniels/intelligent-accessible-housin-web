from frontend.views import *
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

app_name = 'frontend'

urlpatterns = [
    path('login', userLogin, name="login"),
    path('logout/', userLogout, name='logout'),
    path('register', userRegister, name="register"),

    path('', home, name="home"),
    path('about', about, name="about"),
    path('services', services, name="services"),

    path('properties', getProperties, name="getProperties"),
    path('property/<slug:slug>/', showProperty, name="showProperty"),
    path('property/<slug:slug>/apply/', sendRentApplication, name='sendRentApplication'),

    path('user/dashboard', userDashboard, name="userDashboard"),
    path('user/applications/', getUserApplications, name='getUserApplications'),
    path('user/application/<int:application_id>/', showApplicationDetail, name='showApplicationDetail'),

    path('contracts/', getContracts, name='getContracts'),
    path('contract/<int:contract_id>/', showContract, name='showContract'),
    path('contract/accept/<int:contract_id>/', acceptContract, name='acceptContract'),
]  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)