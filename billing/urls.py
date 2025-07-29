from django.urls import path
from . import views

urlpatterns = [
    path('', views.bill_list, name='bill_list'),
    path('create/', views.create_bill, name='create_bill'),
    path('customer-entry/', views.customer_entry, name='customer_entry'),
    path('final-bill/<int:customer_id>/', views.final_bill, name='final_bill'),
    path('final-submit/<int:customer_id>/', views.final_submit_bill, name='final_submit_bill'),
    path('dashboard/', views.cashier_dashboard, name='cashier_dashboard'),
    path('inventory/get_price/<int:product_id>/', views.get_product_price, name='get_product_price'),
]