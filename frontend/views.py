from backend.forms import *
from frontend.forms import *
from backend.models import *
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import authenticate, login as auth_login, logout, update_session_auth_hash

def userLogin(request):
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, _("You have been logged out because you accessed the login page while already logged in."))

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data.get('user')
            auth_login(request, user)
            messages.success(request, _("Welcome back! You have successfully logged in."))
            return redirect(reverse('frontend:userDashboard'))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
            messages.error(request, _("Please address the errors below and try again."))
    else:
        form = LoginForm()

    context = {
        'form': form
    }
    return render(request, 'frontend/pages/auth/login.html', context)

def userLogout(request):
    logout(request)
    messages.success(request, _("You have been successfully logged out."))

    return redirect('frontend:login')

def userRegister(request):
    if request.user.is_authenticated:
        return redirect(reverse('frontend:userDashboard'))
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, _("Your account has been created successfully and you are now logged in."))
            return redirect(reverse('frontend:login'))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
            messages.error(request, _("Please correct the errors below."))
    else:
        form = RegisterForm()

    context = {
        'form': form,
    }
    return render(request, 'frontend/pages/auth/register.html', context)

def userDashboard(request):
    return render(request, 'frontend/pages/user/dashboard.html')

def home(request):
    """
    Home view: Display the homepage with the 4 latest properties.
    """
    properties = Property.objects.order_by('-created_at')[:4]

    context = {
        'properties': properties,
    }

    return render(request, 'frontend/pages/index.html', context)

def getProperties(request):
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

    # --- Dynamic Filter Options ---
    city_choices = Property.CITY_CHOICES
    property_types = Property.TYPE_CHOICES
    property_categories = Property.CATEGORY_CHOICES
    amenities_list = Amenity.objects.all()
    latest_properties = Property.objects.order_by('-created_at')[:4]

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
        'latest_properties': latest_properties,
        'filter_params': request.GET,
        'properties_count': paginator.count,
        'city_choices': city_choices,
        'property_types': property_types,
        'property_categories': property_categories,
        'amenities_list': amenities_list,
        'selected_amenities': selected_amenities,
        'paginator': paginator,
        'page_obj': properties_page,
    }

    return render(request, 'frontend/pages/properties/index.html', context)

def showProperty(request, slug):
    """
    Property detail view:
    - Retrieves a single property based on its slug.
    - Also includes additional data such as review statistics.
    """
    property_obj = get_object_or_404(Property, slug=slug)
    properties = Property.objects.order_by('-created_at')[:4]

    context = {
        'property': property_obj,
        'review_data': property_obj.get_review_data() if hasattr(property_obj, 'get_review_data') else {},
        'properties': properties
    }

    return render(request, 'frontend/pages/properties/show.html', context)