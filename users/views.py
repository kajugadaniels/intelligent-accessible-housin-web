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

@login_required
def search(request):
    if request.user.role not in ['User'] and not request.user.is_superuser:
        raise PermissionDenied(_("You are not authorized to view the dashboard."))

    # On initial GET, load choices from the database
    if request.method == 'GET':
        context = {
            'city_choices': Property.CITY_CHOICES,
            'property_types': Property.TYPE_CHOICES,
            'property_categories': Category.objects.all(),
            'amenities_list': Amenity.objects.all(),
        }
        return render(request, 'backend/pages/users/search.html', context)

    # Handle form submission
    if request.method == 'POST':
        filter_params = {
            'city': request.POST.get('city', ''),
            'type': request.POST.get('type', ''),
            'category': request.POST.get('category', ''),  # now an ID
            'capacity': request.POST.get('capacity', ''),
            'bathroom': request.POST.get('bathroom', ''),
            'size': request.POST.get('size', ''),
            'address': request.POST.get('address', ''),
            'price_min': request.POST.get('price_min', ''),
            'price_max': request.POST.get('price_max', ''),
        }
        # collect amenities IDs
        amenities = request.POST.getlist('amenities')
        if amenities:
            filter_params['amenities'] = amenities

        # build querystring
        qs = '&'.join(f"{k}={v}" for k,v in filter_params.items() if v)
        return redirect(f"{reverse('users:properties')}?{qs}")

@login_required
def properties(request):
    if request.user.role not in ['User'] and not request.user.is_superuser:
        raise PermissionDenied(_("You are not authorized to view the dashboard."))

    filter_params = request.GET
    qs = Property.objects.all()

    # City
    city = filter_params.get('city')
    if city:
        qs = qs.filter(city__iexact=city)

    # Property Type
    prop_type = filter_params.get('type')
    if prop_type:
        qs = qs.filter(type__iexact=prop_type)

    # Category by ID
    category_id = filter_params.get('category')
    if category_id:
        qs = qs.filter(category_id=category_id)

    # Bedrooms
    capacity = filter_params.get('capacity')
    if capacity:
        qs = qs.filter(capacity=capacity)

    # Bathrooms
    bathroom = filter_params.get('bathroom')
    if bathroom:
        qs = qs.filter(bathroom=bathroom)

    # Size (text search)
    size = filter_params.get('size')
    if size:
        qs = qs.filter(size__icontains=size)

    # Address
    address = filter_params.get('address')
    if address:
        qs = qs.filter(address__icontains=address)

    # Price range
    price_min = filter_params.get('price_min')
    if price_min:
        qs = qs.filter(price_usd__gte=price_min)
    price_max = filter_params.get('price_max')
    if price_max:
        qs = qs.filter(price_usd__lte=price_max)

    # Amenities (multiple)
    amenities = filter_params.getlist('amenities')
    if amenities:
        try:
            amenity_ids = [int(a) for a in amenities]
            qs = qs.filter(amenities__id__in=amenity_ids).distinct()
        except ValueError:
            pass  # ignore invalid IDs

    # Sorting
    sort = filter_params.get('sort', '').lower()
    if sort == 'oldest':
        qs = qs.order_by('created_at')
    else:
        qs = qs.order_by('-created_at')

    # Pagination
    limit = 12
    try:
        limit = int(filter_params.get('limit', limit))
    except ValueError:
        pass

    paginator = Paginator(qs, limit)
    page = filter_params.get('page')
    try:
        page_obj = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    return render(request, 'backend/pages/users/properties/index.html', {
        'properties': page_obj,
        'filter_params': filter_params,
        'properties_count': paginator.count,
        'paginator': paginator,
        'page_obj': page_obj,
    })

def notifications(request):
    if request.user.role not in ['User'] and not request.user.is_superuser:
        raise PermissionDenied(_("You are not authorized to view the dashboard."))

    return render(request, 'backend/pages/users/notifications.html')