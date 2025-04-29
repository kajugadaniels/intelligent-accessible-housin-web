from django.shortcuts import render

def dashboard(request):
    return render(request, 'backend/pages/users/dashboard.html')