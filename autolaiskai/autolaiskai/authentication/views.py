from quopri import decodestring
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, authenticate, logout

from authentication.forms import RegisterForm, LoginForm
from .models import CustomUser


def register_view(request, *args, **kwargs):
    user = request.user
    if user.is_authenticated:
        return redirect('/') 
    """ if user.is_authenticated:
        return HttpResponse(f"Prisijungta kaip {user.email}") """
    
    context = {}

    if request.POST:
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email').lower()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(email=email, password=raw_password)
            login(request, user)
            destination = get_redirect_if_exists(request)
            if destination:
                return redirect(destination)
            return redirect("login")
        else:
            context['registration_form'] = form

    return render(request, 'registration/register.html', context)

def login_view(request, *args, **kwargs):
    context = {}

    user = request.user
    if user.is_authenticated:
        return redirect("landing_page")
    
    if request.POST:
        form = LoginForm(request.POST)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email, password = password)
            if user:
                login(request, user)
                destination = get_redirect_if_exists(request)
                if destination:
                    return redirect(destination)
                return redirect("landing_page")
        else:
            context['login_form'] = form
    return render(request, "registration/login.html", context)

def get_redirect_if_exists(request):
    redirect = None
    if request.GET:
        if request.GET.get("next"):
            redirect = str(request.GET.get("next"))
    return redirect


def logout_view(request):
    logout(request)
    return redirect("landing_page")