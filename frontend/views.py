from django.shortcuts import render

def home(request):
    return render(request, 'frontend/pages/index.html')

def getProperties(request):
    return render(request, 'frontend/pages/properties/index.html')

def showProperty(request):
    return render(request, 'frontend/pages/properties/show.html')