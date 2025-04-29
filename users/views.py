from django.db.models import Q
from backend.models import *
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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

    # Retrieve filter parameters from GET request
    filter_params = request.GET

    properties = Property.objects.all()

    # --- Apply Filters ---
    city = filter_params.get('city')
    if city:
        properties = properties.filter(city__iexact=city)

    prop_type = filter_params.get('type')
    if prop_type:
        properties = properties.filter(type__iexact=prop_type)

    category = filter_params.get('category')
    if category:
        properties = properties.filter(category__name__iexact=category)  # Using 'category__name' for ForeignKey

    capacity = filter_params.get('capacity')
    if capacity:
        properties = properties.filter(capacity=capacity)

    bathroom = filter_params.get('bathroom')
    if bathroom:
        properties = properties.filter(bathroom=bathroom)

    size = filter_params.get('size')
    if size:
        properties = properties.filter(size__icontains=size)

    address = filter_params.get('address')
    if address:
        properties = properties.filter(address__icontains=address)

    price_min = filter_params.get('price_min')
    if price_min:
        properties = properties.filter(price_usd__gte=price_min)

    price_max = filter_params.get('price_max')
    if price_max:
        properties = properties.filter(price_usd__lte=price_max)

    # --- Handle Amenities ---
    amenities = filter_params.getlist('amenities')  # Get list of selected amenities
    if amenities:
        try:
            amenities = [int(amenity) for amenity in amenities]  # Convert to integers
            properties = properties.filter(amenities__id__in=amenities).distinct()
        except ValueError:
            pass  # If the conversion fails, we simply don't filter by amenities

    # --- Sorting ---
    sort = filter_params.get('sort')
    if sort:
        if sort.lower() == 'oldest':
            properties = properties.order_by('created_at')
        elif sort.lower() == 'newest':
            properties = properties.order_by('-created_at')
        else:
            properties = properties.order_by('-created_at')

    # --- Pagination ---
    limit = filter_params.get('limit', 12)
    try:
        limit = int(limit)
    except ValueError:
        limit = 12
    paginator = Paginator(properties, limit)
    page = filter_params.get('page')
    try:
        properties_page = paginator.page(page)
    except PageNotAnInteger:
        properties_page = paginator.page(1)
    except EmptyPage:
        properties_page = paginator.page(paginator.num_pages)

    context = {
        'properties': properties_page,
        'filter_params': filter_params,
        'properties_count': paginator.count,
        'paginator': paginator,
        'page_obj': properties_page,
    }

    return render(request, 'backend/pages/users/properties/index.html', context)

@login_required
def getAgents(request):
    if not (request.user.role == 'User'):
        raise PermissionDenied(_("You are not authorized to access the House Providers page."))

    houseProviders = User.objects.filter(role='House Provider').order_by('-created_at')

    context = {
        'houseProviders': houseProviders
    }

    return render(request, 'backend/pages/users/agents/index.html', context)