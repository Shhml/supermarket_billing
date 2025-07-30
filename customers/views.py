from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Customer
from .forms import CustomerForm

@login_required
def customer_list(request):
    """Display list of all customers"""
    customers = Customer.objects.all().order_by('name')
    return render(request, 'customers/customer_list.html', {'customers': customers})

@login_required
def customer_add(request):
    """Add a new customer"""
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer added successfully!')
            return redirect('customers:customer_list')
    else:
        form = CustomerForm()
    
    return render(request, 'customers/customer_form.html', {'form': form, 'title': 'Add Customer'})

@login_required
def customer_edit(request, pk):
    """Edit an existing customer"""
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer updated successfully!')
            return redirect('customers:customer_list')
    else:
        form = CustomerForm(instance=customer)
    
    return render(request, 'customers/customer_form.html', {
        'form': form, 
        'title': 'Edit Customer',
        'customer': customer
    })

@login_required
def customer_delete(request, pk):
    """Delete a customer"""
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'Customer deleted successfully!')
        return redirect('customers:customer_list')
    
    return render(request, 'customers/customer_confirm_delete.html', {'customer': customer})

@login_required
def customer_detail(request, pk):
    """Display customer details"""
    customer = get_object_or_404(Customer, pk=pk)
    return render(request, 'customers/customer_detail.html', {'customer': customer})
