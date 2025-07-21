from django.shortcuts import render

# Create your views here.


# ==============================
# Import necessary modules
# ==============================

from django.views.generic import ListView
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from .models import Product

def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

@method_decorator(user_passes_test(is_admin), name='dispatch')
class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Product.objects.filter(name__icontains=query) | Product.objects.filter(barcode__icontains=query)
        return Product.objects.all()


#======================================
# Create a view for adding new products
#======================================

from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .models import Product
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator

def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

@method_decorator(user_passes_test(is_admin), name='dispatch')
class ProductCreateView(CreateView):
    model = Product
    fields = ['name', 'barcode', 'category', 'price', 'description']
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('product_list')


#======================================
# Create a view for editing products
#======================================

from django.views.generic.edit import UpdateView
from .models import Product
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy

@method_decorator(user_passes_test(is_admin), name='dispatch')
class ProductUpdateView(UpdateView):
    model = Product
    fields = ['name', 'barcode', 'category', 'price', 'description']
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('product_list')


#======================================
# Create a view for conforming deleting products
#======================================

from django.views.generic.edit import DeleteView
from .models import Product

@method_decorator(user_passes_test(is_admin), name='dispatch')
class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('product_list')
