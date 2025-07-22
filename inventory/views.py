from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView
from .models import Inventory
from products.models import Product
from django.urls import reverse_lazy
from users.decorators import role_required
from django.utils.decorators import method_decorator

# View Inventory List
class InventoryListView(ListView):
    model = Inventory
    template_name = 'inventory/inventory_list.html'
    context_object_name = 'inventory_list'

# Add Inventory (Admin only)
@method_decorator(role_required('admin'), name='dispatch')
class InventoryCreateView(CreateView):
    model = Inventory
    fields = ['product', 'quantity', 'restock_threshold']
    template_name = 'inventory/inventory_form.html'
    success_url = reverse_lazy('inventory_list')

# Edit Inventory (Admin only)
@method_decorator(role_required('admin'), name='dispatch')
class InventoryUpdateView(UpdateView):
    model = Inventory
    fields = ['quantity', 'restock_threshold']
    template_name = 'inventory/inventory_form.html'
    success_url = reverse_lazy('inventory_list')
