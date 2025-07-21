from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from .forms import CustomLoginForm

class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'users/login.html'

    def get_success_url(self):
        user = self.request.user
        if user.is_authenticated:
            if user.role == 'admin':
                return reverse_lazy('admin_dashboard')
            elif user.role == 'cashier':
                return reverse_lazy('cashier_dashboard')
        return reverse_lazy('login')

@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        return redirect('cashier_dashboard')
    return render(request, 'users/admin_dashboard.html', {'user': request.user})

@login_required
def cashier_dashboard(request):
    if request.user.role != 'cashier':
        return redirect('admin_dashboard')
    return render(request, 'users/cashier_dashboard.html', {'user': request.user})

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')