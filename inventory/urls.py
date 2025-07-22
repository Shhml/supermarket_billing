from django.urls import path
from .views import InventoryListView, InventoryCreateView, InventoryUpdateView

urlpatterns = [
    path('', InventoryListView.as_view(), name='inventory_list'),
    path('add/', InventoryCreateView.as_view(), name='inventory_add'),
    path('<int:pk>/edit/', InventoryUpdateView.as_view(), name='inventory_edit'),
]
