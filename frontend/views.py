from django.shortcuts import render

def home(request):
    return render(request, 'frontend/pages/index.html')

def getProperties(request):
    return render(request, 'frontend/pages/property.html')