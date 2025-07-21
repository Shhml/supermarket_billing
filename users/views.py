from django.shortcuts import render

# Create your views here.
from django.shortcuts import redirect

def redirect_to_login(request):
    return redirect('login')


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.role == 'admin':
                return redirect('admin_dashboard')
            elif user.role == 'cashier':
                return redirect('cashier_dashboard')
            else:
                messages.error(request, "Unknown role assigned.")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'login.html')

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

@login_required
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

@login_required
def cashier_dashboard(request):
    return render(request, 'cashier_dashboard.html')

