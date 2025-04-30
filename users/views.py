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

    params = request.GET
    qs = Property.objects.all()

    # City
    city = params.get('city')
    if city:
        qs = qs.filter(city__iexact=city)

    # Property Type
    prop_type = params.get('type')
    if prop_type:
        qs = qs.filter(type__iexact=prop_type)

    # Category by ID
    cat = params.get('category')
    if cat:
        try:
            qs = qs.filter(category_id=int(cat))
        except ValueError:
            pass

    # Bedrooms <=
    capacity = params.get('capacity')
    if capacity:
        try:
            qs = qs.filter(capacity__lte=int(capacity))
        except ValueError:
            pass

    # Bathrooms <=
    bathroom = params.get('bathroom')
    if bathroom:
        try:
            qs = qs.filter(bathroom__lte=int(bathroom))
        except ValueError:
            pass

    # Size (assumes `size` stores a plain number as string)
    size_val = params.get('size')
    if size_val:
        try:
            max_size = int(size_val)
            qs = qs.annotate(
                size_int=Cast('size', IntegerField())
            ).filter(size_int__lte=max_size)
        except ValueError:
            pass

    # Address contains
    address = params.get('address')
    if address:
        qs = qs.filter(address__icontains=address)

    # Price range
    price_min = params.get('price_min')
    if price_min:
        try:
            qs = qs.filter(price_usd__gte=int(price_min))
        except ValueError:
            pass

    price_max = params.get('price_max')
    if price_max:
        try:
            qs = qs.filter(price_usd__lte=int(price_max))
        except ValueError:
            pass

    # Amenities ⩽
    amenities = params.getlist('amenities')
    if amenities:
        try:
            amenity_ids = [int(a) for a in amenities]
            qs = qs.filter(amenities__id__in=amenity_ids).distinct()
        except ValueError:
            pass

    # Sorting
    sort = params.get('sort', '').lower()
    if sort == 'oldest':
        qs = qs.order_by('created_at')
    else:
        qs = qs.order_by('-created_at')

    # Pagination
    try:
        limit = int(params.get('limit', 12))
    except ValueError:
        limit = 12

    paginator = Paginator(qs, limit)
    page = params.get('page')
    try:
        page_obj = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    context = {
        'properties': page_obj,
        'filter_params': params,
        'properties_count': paginator.count,
        'paginator': paginator,
        'page_obj': page_obj,
    }

    return render(request, 'backend/pages/users/properties/index.html', context)

@login_required
def notifications(request):
    if request.user.role not in ['User'] and not request.user.is_superuser:
        raise PermissionDenied(_("You are not authorized to view the dashboard."))

    return render(request, 'backend/pages/users/notifications.html')

@login_required
def sendApplication(request):
    if request.user.role not in ['User'] and not request.user.is_superuser:
        raise PermissionDenied(_("You are not authorized to view the dashboard."))

    return render(request, 'backend/pages/users/rent-applications/create.html')