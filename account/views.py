import logging
from home.models import *
from account.forms import *
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout

logger = logging.getLogger(__name__)

def user_login(request):
    if request.user.is_authenticated:
        return redirect('home:dashboard')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data.get('phone_number')
            password = form.cleaned_data.get('password')
            academic_year_id = form.cleaned_data.get('academic_year').id  # Get the ID, not the object
            user = authenticate(request, phone_number=phone_number, password=password)

            if user is not None:
                if user.is_active:
                    auth_login(request, user)
                    request.session['academic_year_id'] = academic_year_id  # Store only the ID
                    messages.success(request, _('Login successful!'))
                    return redirect('home:dashboard')
                else:
                    messages.error(request, _('Your account is inactive.'))
            else:
                messages.error(request, _('Invalid phone number or password'))
        else:
            # Log and show form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
            logger.warning(f"Login form validation errors: {form.errors}")
    else:
        form = LoginForm()

    academic_years = AcademicYear.objects.filter(delete_status=False).order_by('-start_date')

    context = {
        'form': form,
        'academic_years': academic_years
    }

    return render(request, 'pages/auth/login.html', context)