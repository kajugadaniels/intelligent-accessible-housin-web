import random
from backend.forms import *
from backend.models import *
from frontend.models import *
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout, update_session_auth_hash

@login_required
def getAmenities(request):
    # Only House Providers may access amenities pages.
    if request.user.role != 'House Provider':
        raise PermissionDenied(_("You are not authorized to access the Amenities page."))

    amenities = Amenity.objects.all().order_by('-created_at')

    context = {
        'amenities': amenities
    }

    return render(request, 'backend/pages/agents/amenities/index.html', context)