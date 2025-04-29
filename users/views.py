from backend.models import *
from django.shortcuts import render
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

    properties = Property.objects.all()

    # --- Filtering ---
    city = request.GET.get('city')
    if city:
        properties = properties.filter(city__iexact=city)

    prop_type = request.GET.get('type')
    if prop_type:
        properties = properties.filter(type__iexact=prop_type)

    category = request.GET.get('category')
    if category:
        properties = properties.filter(category__iexact=category)

    capacity = request.GET.get('capacity')
    if capacity:
        properties = properties.filter(capacity=capacity)

    bathroom = request.GET.get('bathroom')
    if bathroom:
        properties = properties.filter(bathroom=bathroom)

    size = request.GET.get('size')
    if size:
        properties = properties.filter(size__icontains=size)

    address = request.GET.get('address')
    if address:
        properties = properties.filter(address__icontains=address)

    price_min = request.GET.get('price_min')
    if price_min:
        properties = properties.filter(price_usd__gte=price_min)

    price_max = request.GET.get('price_max')
    if price_max:
        properties = properties.filter(price_usd__lte=price_max)

    # --- Filtering by Multiple Amenities ---
    selected_amenities = request.GET.getlist('amenities')
    if selected_amenities:
        properties = properties.filter(amenities__id__in=selected_amenities).distinct()

    # --- Sorting ---
    sort = request.GET.get('sort')
    if sort:
        if sort.lower() == 'oldest':
            properties = properties.order_by('created_at')
        elif sort.lower() == 'newest':
            properties = properties.order_by('-created_at')
        else:
            properties = properties.order_by('-created_at')
    else:
        properties = properties.order_by('-created_at')

    # --- Pagination ---
    limit = request.GET.get('limit', 12)
    try:
        limit = int(limit)
    except ValueError:
        limit = 12
    paginator = Paginator(properties, limit)
    page = request.GET.get('page')
    try:
        properties_page = paginator.page(page)
    except PageNotAnInteger:
        properties_page = paginator.page(1)
    except EmptyPage:
        properties_page = paginator.page(paginator.num_pages)

    context = {
        'properties': properties_page,
        'filter_params': request.GET,
        'properties_count': paginator.count,
        'city_choices': Property.CITY_CHOICES,
        'property_types': Property.TYPE_CHOICES,
        'property_categories': Property.CATEGORY_CHOICES,
        'amenities_list': Amenity.objects.all(),
        'selected_amenities': selected_amenities,
        'paginator': paginator,
        'page_obj': properties_page,
    }

    return render(request, 'backend/pages/users/properties/index.html', context)

def properties(request):
    if request.user.role not in ['User'] and not request.user.is_superuser:
        raise PermissionDenied(_("You are not authorized to view the dashboard."))

    return render(request, 'backend/pages/users/properties/index.html')