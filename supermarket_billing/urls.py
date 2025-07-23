from django.contrib import admin
from django.urls import path, include
from users import views as user_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', user_views.redirect_to_login),  # Redirect root to /login/
    path('', include('users.urls')),
    path('admin-dashboard/', user_views.admin_dashboard, name='admin_dashboard'),
    path('cashier-dashboard/', user_views.cashier_dashboard, name='cashier_dashboard'),
    path('products/', include('products.urls')),
    path('inventory/', include('inventory.urls')),
    path('billing/', include('billing.urls')),
    


]
