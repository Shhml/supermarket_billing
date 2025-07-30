from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from .forms import CustomLoginForm

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


from django.db.models import Sum, F
from django.utils.timezone import now
from billing.models import Bill
from inventory.models import Inventory
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def admin_dashboard(request):
    today = now().date()

    total_sales_today = Bill.objects.filter(
        created_at__date=today
    ).aggregate(total_sales=Sum('total_amount'))['total_sales'] or 0

    total_bills_today = Bill.objects.filter(
        created_at__date=today
    ).count()

    low_stock_count = Inventory.objects.filter(
        quantity__lt=F('restock_threshold')
    ).count()

    return render(request, 'admin_dashboard.html', {
        'total_sales_today': total_sales_today,
        'total_bills_today': total_bills_today,
        'low_stock_count': low_stock_count,
    })


@login_required
def cashier_dashboard(request):
    return render(request, 'cashier_dashboard.html')

from django.contrib.auth import logout
from django.shortcuts import redirect

def user_logout(request):
    logout(request)
    return redirect('login')
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User

@login_required
def create_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        
        # Handle AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            if form.is_valid():
                user = form.save()
                return JsonResponse({
                    'success': True, 
                    'message': f'User "{user.username}" created successfully!'
                })
            else:
                return JsonResponse({
                    'success': False, 
                    'errors': form.errors
                })
        
        # Handle regular form submission
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User "{user.username}" created successfully!')
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()
    
    return render(request, 'create_user.html', {'form': form})