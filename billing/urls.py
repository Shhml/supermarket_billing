from django.urls import path
from . import views

urlpatterns = [
    path('', views.bill_list, name='bill_list'),
    path('create/', views.create_bill, name='create_bill'),
]
