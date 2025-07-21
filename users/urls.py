from django.urls import path
from .views import CustomLoginView, admin_dashboard, cashier_dashboard, CustomLogoutView

urlpatterns = [
    path('', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('dashboard/admin/', admin_dashboard, name='admin_dashboard'),
    path('dashboard/cashier/', cashier_dashboard, name='cashier_dashboard'),
]