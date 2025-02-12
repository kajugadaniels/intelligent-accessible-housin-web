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

# --------------------------------
# Authentication and profile views
# --------------------------------

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
            return redirect(reverse('backend:dashboard'))
        else:
            # Extract and display form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
            messages.error(request, _("Please address the errors below and try again."))
    else:
        form = LoginForm()

    context = {
        'form': form
    }

    return render(request, 'backend/pages/auth/login.html', context)


def userLogout(request):
    logout(request)
    messages.success(request, _("You have been successfully logged out."))

    return redirect('backend:login')


@login_required
def userProfile(request):
    # Profile page: accessible for all logged-in users.
    user = request.user
    profile_form = UserProfileForm(instance=user)
    password_form = PasswordChangeForm(user=user)

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            profile_form = UserProfileForm(request.POST, request.FILES, instance=user)
            if profile_form.is_valid():
                # Delete old image if a new one is uploaded
                if 'image' in request.FILES and user.image:
                    user.image.delete(save=False)
                profile_form.save()
                messages.success(request, _("Your profile has been updated successfully."))
                return redirect('backend:userProfile')
            else:
                messages.error(request, _("Please correct the errors in the profile form and try again."))
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                new_password = password_form.cleaned_data.get('new_password')
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, _("Your password has been changed successfully."))
                return redirect('backend:userProfile')
            else:
                messages.error(request, _("Please correct the errors in the password form and try again."))

    context = {
        'profile_form': profile_form,
        'password_form': password_form,
    }

    return render(request, 'backend/pages/auth/profile.html', context)


# -------------------------------
# Dashboard
# -------------------------------

@login_required
def dashboard(request):
    # Only Admin and House Provider are allowed to access the dashboard.
    if request.user.role not in ['Admin', 'House Provider'] and not request.user.is_superuser:
        raise PermissionDenied(_("You are not authorized to view the dashboard."))

    return render(request, 'backend/pages/dashboard.html')


# -------------------------------
# Admin-only views (Agents, Rentals, Leases, Applications)
# -------------------------------

@login_required
def getHouseProviders(request):
    # Only Admin (or superuser) may view House Providers
    if not (request.user.role == 'Admin'):
        raise PermissionDenied(_("You are not authorized to access the House Providers page."))

    houseProviders = User.objects.filter(role='House Provider').order_by('-created_at')

    context = {
        'houseProviders': houseProviders
    }

    return render(request, 'backend/pages/houseProviders/index.html', context)


@login_required
def addHouseProvider(request):
    if not (request.user.role == 'Admin'):
        raise PermissionDenied(_("You are not authorized to add a House Provider."))

    if request.method == 'POST':
        form = HouseProviderUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user_instance = form.save()
            messages.success(request, _("House Provider '%(name)s' has been created successfully.") % {'name': user_instance.name})
            return redirect(reverse('backend:getHouseProviders'))
        else:
            messages.error(request, _("Please correct the errors below."))
    else:
        form = HouseProviderUserCreationForm()

    context = {
        'form': form,
        'title': _('Add House Provider')
    }

    return render(request, 'backend/pages/houseProviders/create.html', context)


@login_required
def showHouseProvider(request, id):
    if not (request.user.role == 'Admin'):
        raise PermissionDenied(_("You are not authorized to view this House Provider."))

    houseProvider = get_object_or_404(User, id=id, role='House Provider')

    context = {
        'houseProvider': houseProvider,
        'title': _("House Provider: %(name)s") % {'name': houseProvider.name}
    }

    return render(request, 'backend/pages/houseProviders/show.html', context)


@login_required
def editHouseProvider(request, id):
    if not (request.user.role == 'Admin'):
        raise PermissionDenied(_("You are not authorized to edit this House Provider."))

    houseProvider = get_object_or_404(User, id=id, role='House Provider')
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=houseProvider)
        if form.is_valid():
            form.save()
            messages.success(request, _("House Provider '%(name)s' has been updated successfully.") % {'name': houseProvider.name})
            return redirect(reverse('backend:getHouseProviders'))
        else:
            messages.error(request, _("Please correct the errors below and try again."))
    else:
        form = UserProfileForm(instance=houseProvider)

    context = {
        'form': form,
        'title': _("Edit House Provider: %(name)s") % {'name': houseProvider.name}
    }

    return render(request, 'backend/pages/houseProviders/edit.html', context)


@login_required
def deleteHouseProvider(request, id):
    if not (request.user.role == 'Admin'):
        raise PermissionDenied(_("You are not authorized to delete this House Provider."))

    houseProvider = get_object_or_404(User, id=id, role='House Provider')

    if request.method == 'POST':
        houseProvider.delete()
        messages.success(request, _("House Provider '%(name)s' has been deleted successfully.") % {'name': houseProvider.name})
        return redirect(reverse('backend:getHouseProviders'))

    context = {
        'houseProvider': houseProvider
    }

    return render(request, 'backend/pages/houseProviders/delete.html', context)


@login_required
def getRentals(request):
    # Rentals page: Admin-only (or superuser)
    if not (request.user.role == 'Admin'):
        raise PermissionDenied(_("You are not authorized to view the Rentals page."))

    return render(request, 'backend/pages/rentals/index.html')


@login_required
def getLeases(request):
    # Leases page: Admin-only (or superuser)
    if not (request.user.role == 'Admin'):
        raise PermissionDenied(_("You are not authorized to view the Leases page."))

    return render(request, 'backend/pages/leases/index.html')


@login_required
def getApplications(request):
    # Applications page: Admin-only (or superuser)
    if not (request.user.role == 'Admin'):
        raise PermissionDenied(_("You are not authorized to view the Applications page."))

    return render(request, 'backend/pages/applications/index.html')


# -------------------------------
# House Provider-only views (Amenities, Properties, Notifications)
# -------------------------------

@login_required
def getAmenities(request):
    # Only House Providers may access amenities pages.
    if request.user.role != 'House Provider':
        raise PermissionDenied(_("You are not authorized to access the Amenities page."))

    amenities = Amenity.objects.all().order_by('-created_at')

    context = {
        'amenities': amenities
    }

    return render(request, 'backend/pages/amenities/index.html', context)


@csrf_exempt
@login_required
def addAmenity(request):
    if request.user.role != 'House Provider':
        raise PermissionDenied(_("You are not authorized to add an Amenity."))

    if request.method == 'POST':
        form = AmenityForm(request.POST)
        if form.is_valid():
            amenity = form.save(commit=False)
            amenity.created_by = request.user
            amenity.save()
            form.save_m2m()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'id': amenity.id, 'name': amenity.name})
            else:
                messages.success(request, _("The amenity '%(amenity)s' has been created successfully.") % {'amenity': amenity.name})
                return redirect(reverse('backend:getAmenities'))
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'errors': form.errors}, status=400)
            else:
                messages.error(request, _("Please correct the errors below and try again."))
    else:
        form = AmenityForm()

    context = {
        'form': form,
        'title': _('Add New Amenity')
    }
    return render(request, 'backend/pages/amenities/create.html', context)


@login_required
def showAmenity(request, id):
    if request.user.role != 'House Provider':
        raise PermissionDenied(_("You are not authorized to view this Amenity."))

    amenity = get_object_or_404(Amenity, id=id)

    context = {
        'amenity': amenity,
        'title': _('Amenity: %(amenity)s') % {'amenity': amenity.name},
    }

    return render(request, 'backend/pages/amenities/show.html', context)


@login_required
def editAmenity(request, id):
    if request.user.role != 'House Provider':
        raise PermissionDenied(_("You are not authorized to edit this Amenity."))

    amenity = get_object_or_404(Amenity, id=id)

    if request.method == 'POST':
        form = AmenityForm(request.POST, instance=amenity)
        if form.is_valid():
            amenity = form.save()
            messages.success(request, _("The amenity '%(amenity)s' has been updated successfully.") % {'amenity': amenity.name})
            return redirect(reverse('backend:getAmenities'))
        else:
            messages.error(request, _("Please correct the errors below and try again."))
    else:
        form = AmenityForm(instance=amenity)

    context = {
        'form': form,
        'title': _('Edit amenity: %(amenity)s') % {'amenity': amenity.name}
    }

    return render(request, 'backend/pages/amenities/edit.html', context)


@login_required
def deleteAmenity(request, id):
    if request.user.role != 'House Provider':
        raise PermissionDenied(_("You are not authorized to delete this Amenity."))

    amenity = get_object_or_404(Amenity, id=id)

    if request.method == 'POST':
        amenity.delete()
        messages.success(request, _("The amenity '%(amenity)s' has been deleted successfully.") % {'amenity': amenity.name})
        return redirect(reverse('backend:getAmenities'))

    context = {
        'amenity': amenity
    }

    return render(request, 'backend/pages/amenities/delete.html', context)

@login_required
def getProperties(request):
    if request.user.role != 'House Provider':
        raise PermissionDenied(_("You are not authorized to access the Properties page."))

    properties = Property.objects.filter(created_by=request.user).order_by('-created_at')

    context = {
        'properties': properties
    }

    return render(request, 'backend/pages/properties/index.html', context)

@login_required
def addProperty(request):
    if request.user.role != 'House Provider':
        raise PermissionDenied(_("You are not authorized to add a Property."))

    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the property instance
            property_instance = form.save(commit=False)
            property_instance.created_by = request.user
            property_instance.save()
            form.save_m2m()

            # Add the main property image to PropertyImage model (if provided)
            if property_instance.image:
                PropertyImage.objects.create(property=property_instance, image=property_instance.image)

            # Process additional images from the "Additional Images" input
            additional_images = request.FILES.getlist('images')
            for img in additional_images:
                PropertyImage.objects.create(property=property_instance, image=img)

            messages.success(
                request,
                _("The property '%(property)s' has been created successfully.") % {'property': property_instance.name}
            )
            return redirect(reverse('backend:getProperties'))
        else:
            messages.error(request, _("Please correct the errors below and try again."))
    else:
        form = PropertyForm()

    context = {
        'form': form,
        'title': _('Add New Property')
    }

    return render(request, 'backend/pages/properties/create.html', context)

@login_required
def showProperty(request, id):
    if request.user.role != 'House Provider':
        raise PermissionDenied(_("You are not authorized to view this Property."))

    property_instance = get_object_or_404(Property, id=id, created_by=request.user)

    context = {
        'property': property_instance,
        'title': _('Property: %(property)s') % {'property': property_instance.name}
    }

    return render(request, 'backend/pages/properties/show.html', context)


@login_required
def editProperty(request, id):
    if request.user.role != 'House Provider':
        raise PermissionDenied(_("You are not authorized to edit this Property."))

    property_instance = get_object_or_404(Property, id=id, created_by=request.user)

    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property_instance)
        if form.is_valid():
            property_instance = form.save()
            # Process additional new images (if any)
            images = request.FILES.getlist('images')
            for img in images:
                PropertyImage.objects.create(property=property_instance, image=img)
            messages.success(request, _("The property '%(property)s' has been updated successfully.") % {'property': property_instance.name})
            return redirect(reverse('backend:getProperties'))
        else:
            messages.error(request, _("Please correct the errors below and try again."))
    else:
        form = PropertyForm(instance=property_instance)

    context = {
        'form': form,
        'property': property_instance,
        'title': _('Edit Property: %(property)s') % {'property': property_instance.name}
    }

    return render(request, 'backend/pages/properties/edit.html', context)

@login_required
def deletePropertyImage(request, image_id):
    """
    Deletes an additional image via AJAX.
    Expects a POST request with proper CSRF token.
    """
    image_instance = get_object_or_404(PropertyImage, id=image_id, property__created_by=request.user)
    if request.method == 'POST':
        property_id = image_instance.property.id
        image_instance.delete()
        return JsonResponse({
            'success': True,
            'message': _("The image has been deleted successfully."),
            'property_id': property_id,
        })
    return JsonResponse({'error': _('Invalid request.')}, status=400)

@login_required
def deleteProperty(request, id):
    if request.user.role != 'House Provider':
        raise PermissionDenied(_("You are not authorized to delete this Property."))

    property_instance = get_object_or_404(Property, id=id, created_by=request.user)

    if request.method == 'POST':
        property_instance.delete()
        messages.success(request, _("The property '%(property)s' has been deleted successfully.") % {'property': property_instance.name})
        return redirect(reverse('backend:getProperties'))

    context = {
        'property': property_instance
    }

    return render(request, 'backend/pages/properties/delete.html', context)

@login_required
def getNotifications(request):
    # Notifications page: allowed only for House Providers.
    if request.user.role != 'House Provider':
        raise PermissionDenied(_("You are not authorized to view the Notifications page."))

    return render(request, 'backend/pages/notifications/index.html')

@login_required
def getRentApplications(request):
    """
    View to get rent applications.
    - Admin can see all applications.
    - House Providers can only see applications for properties they created.
    """
    if request.user.role == 'Admin':
        # Admin can see all rent applications
        applications = RentApplication.objects.all().order_by('-created_at')
    elif request.user.role == 'House Provider':
        # House Provider can only see applications for properties they created
        applications = RentApplication.objects.filter(property__created_by=request.user).order_by('-created_at')
    else:
        raise PermissionDenied(_("You are not authorized to access the applications page."))

    context = {
        'applications': applications
    }

    return render(request, 'backend/pages/applications/index.html', context)

@login_required
def showApplication(request, id):
    """
    View to show rent application details.
    - Admin and House Provider can view details of applications.
    - Only Admin or House Providers who created the property can update the application status.
    """
    application = get_object_or_404(RentApplication, id=id)

    # Check if the user is authorized to view the application
    if request.user.role == 'Admin' or application.property.created_by == request.user:
        if request.method == 'POST':
            # Handle status change based on the form submission
            new_status = request.POST.get('status')
            if new_status in ['Accepted', 'Rejected', 'Moved Out']:
                application.status = new_status
                application.save()
                messages.success(request, _("The application status has been updated to '%s' successfully.") % new_status)
            else:
                messages.error(request, _("Invalid status update."))

            return redirect('backend:showApplication', id=application.id)
    else:
        raise PermissionDenied(_("You do not have permission to view or update this application."))

    context = {
        'application': application,
        'title': _('Application for %(property)s') % {'property': application.property.name}
    }

    return render(request, 'backend/pages/applications/show.html', context)

@login_required
def updateApplicationStatus(request, id):
    """
    View to update rent application status.
    - Admin can update the status of any application.
    - House Provider can only update the status for applications made to properties they created.
    """
    application = get_object_or_404(RentApplication, id=id)

    # Check if the user is authorized to update the application status
    if request.user.role == 'Admin' or application.property.created_by == request.user:
        if request.method == 'POST':
            # Get the selected status from the form
            status = request.POST.get('status')

            # Ensure the status is valid
            if status not in ['Accepted', 'Rejected', 'Moved Out']:
                messages.error(request, "Invalid status.")
                return redirect('backend:showApplication', id=id)

            # Update the application's status
            application.status = status
            application.save()

            messages.success(request, f"Application status updated to {status}.")
            return redirect('backend:showApplication', id=id)
    else:
        raise PermissionDenied(_("You do not have permission to perform this action."))

    context = {
        'application': application,
    }

    return render(request, 'backend/pages/applications/edit.html', context)

@login_required
def getContracts(request):
    if request.user.role == 'Admin':
        contracts = Contract.objects.all()
    elif request.user.role == 'House Provider':
        contracts = Contract.objects.filter(property__created_by=request.user)
    else:
        contracts = []
        messages.error(request, "You are not authorized to view contracts.")
    
    context = {
        'contracts': contracts
    }

    return render(request, 'backend/pages/contracts/index.html', context)

@login_required
def createContract(request, rent_application_id):
    rent_application = get_object_or_404(RentApplication, id=rent_application_id, status='Accepted')
    if request.method == 'POST':
        form = ContractForm(request.POST, rent_application=rent_application)
        if form.is_valid():
            contract = form.save()
            messages.success(request, f"Contract #{contract.contract_number} created successfully!")
            return redirect('backend:show_contract', contract.id)
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = ContractForm(rent_application=rent_application)

    context = {
        'form': form,
        'title': 'Create Contract'
    }

    return render(request, 'backend/pages/contracts/create.html', context)