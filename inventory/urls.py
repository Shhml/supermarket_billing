from django.urls import path
from .views import InventoryListView, InventoryCreateView, InventoryUpdateView
from . import views


urlpatterns = [
    path('', InventoryListView.as_view(), name='inventory_list'),
    path('add/', InventoryCreateView.as_view(), name='inventory_add'),
    path('<int:pk>/edit/', InventoryUpdateView.as_view(), name='inventory_edit'),
    path('get_price/<int:product_id>/', views.get_product_price, name='get_product_price'),
]

