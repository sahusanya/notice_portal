from django.shortcuts import render

# Create your views here.

def home(request):
    return render(request, 'home.html')

def dashboard(request):
    return render(request, 'dashboard.html')

def generate_notice(request):
    return render(request, 'generate_notice.html')

def manage_templates(request):
    return render(request, 'manage_templates.html')

def manage_companies(request):
    return render(request, 'manage_companies.html')
