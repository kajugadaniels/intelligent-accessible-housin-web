from backend.models import *
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

def dashboard(request):
    if request.user.role not in ['User'] and not request.user.is_superuser:
        raise PermissionDenied(_("You are not authorized to view the dashboard."))

    return render(request, 'backend/pages/users/dashboard.html')

def search(request):
    if request.user.role not in ['User'] and not request.user.is_superuser:
        raise PermissionDenied(_("You are not authorized to view the dashboard."))

    if request.method == 'GET':
        context = {
            'city_choices': Property.CITY_CHOICES,
            'property_types': Property.TYPE_CHOICES,
            'property_categories': Property.CATEGORY_CHOICES,
            'amenities_list': Amenity.objects.all(),
        }
        return render(request, 'backend/pages/users/search.html', context)

    # If the form is submitted (via GET method), we'll filter properties based on the provided criteria.
    if request.method == 'POST':
        city = request.POST.get('city')
        prop_type = request.POST.get('type')
        category = request.POST.get('category')
        capacity = request.POST.get('capacity')
        bathroom = request.POST.get('bathroom')
        size = request.POST.get('size')
        address = request.POST.get('address')
        price_min = request.POST.get('price_min')
        price_max = request.POST.get('price_max')
        amenities = request.POST.getlist('amenities')

        # Create a dictionary for query parameters to pass to the properties function
        filter_params = {
            'city': city,
            'type': prop_type,
            'category': category,
            'capacity': capacity,
            'bathroom': bathroom,
            'size': size,
            'address': address,
            'price_min': price_min,
            'price_max': price_max,
            'amenities': amenities,
        }

        return redirect(reverse('users:properties') + '?' + '&'.join([f'{k}={v}' for k, v in filter_params.items() if v]))

def properties(request):
    if request.user.role not in ['User'] and not request.user.is_superuser:
        raise PermissionDenied(_("You are not authorized to view the dashboard."))

    return render(request, 'backend/pages/users/properties/index.html')