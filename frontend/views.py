from backend.models import *
from django.shortcuts import render, get_object_or_404

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
    return render(request, 'frontend/pages/properties/index.html')

def showProperty(request):
    return render(request, 'frontend/pages/properties/show.html')