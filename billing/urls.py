from django.urls import path
from . import views

urlpatterns = [
    path('', views.bill_list, name='bill_list'),
    path('create/', views.create_bill, name='create_bill'),
    path('billing/create/', views.create_bill, name='create_bill'),
    path('billing/customer/<int:customer_id>/', views.check_customer, name='check_customer'),
    path('billing/customer-entry/', views.customer_entry, name='customer_entry'),
    path('billing/customer/<int:customer_id>/', views.customer_summary, name='customer_summary'),
    path('billing/final-submit/<int:customer_id>/', views.final_submit_bill, name='final_submit_bill'),
    path('billing/final-bill/<int:customer_id>/', views.final_bill, name='final_bill'),






]
