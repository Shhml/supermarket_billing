from django.shortcuts import render, redirect, get_object_or_404
from django.forms import formset_factory
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Bill, BillItem
from .forms import BillForm, BillItemForm
from inventory.models import Inventory
from customers.models import Customer
from products.models import Product
from django.db import models
import uuid
from decimal import Decimal

def generate_bill_number():
    return f"BILL-{uuid.uuid4().hex[:8].upper()}"

@login_required
def create_bill(request):
    BillItemFormSet = formset_factory(BillItemForm, extra=1)

    if request.method == 'POST':
        bill_form = BillForm(request.POST)
        formset = BillItemFormSet(request.POST)
        action = request.POST.get('action')
        if action == 'proceed_to_customer' and bill_form.is_valid() and formset.is_valid():
            # Save bill as draft
            bill = bill_form.save(commit=False)
            bill.cashier = request.user
            bill.bill_number = generate_bill_number()
            bill.total_amount = Decimal('0')
            bill.status = 'draft'
            bill.save()

            # Save bill items and calculate total
            for form in formset:
                if form.cleaned_data:
                    bill_item = form.save(commit=False)
                    product = bill_item.product
                    inventory = get_object_or_404(Inventory, product=product)
                    if inventory.quantity < bill_item.quantity:
                        bill.delete()
                        messages.error(request, f"Not enough stock for '{product.name}'.")
                        return redirect('create_bill')
                    bill_item.bill = bill
                    bill_item.price_at_purchase = product.price
                    bill_item.save()
                    bill.total_amount += bill_item.total_price
            bill.total_amount -= bill.discount
            bill.save()

            request.session['bill_id'] = bill.id
            return redirect('customer_entry')
        else:
            messages.error(request, "Please correct the form errors.")
    else:
        bill_form = BillForm()
        formset = BillItemFormSet()
        generated_bill_number = generate_bill_number()

    return render(request, 'billing/bill_form.html', {
        'bill_form': bill_form,
        'formset': formset,
        'bill_number': generated_bill_number
    })

@login_required
def customer_entry(request):
    bill_id = request.session.get('bill_id')
    if not bill_id:
        messages.error(request, "No bill in progress.")
        return redirect('create_bill')

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'search_customer':
            search_query = request.POST.get('search_query')
            if search_query:
                customers = Customer.objects.filter(
                    models.Q(name__icontains=search_query) | models.Q(phone__icontains=search_query)
                )
                # Calculate eligible discount for each customer
                customers_with_discount = [
                    {'customer': c, 'discount': c.loyalty_points // 10}
                    for c in customers
                ]
                return render(request, 'customers/customer_entry.html', {
                    'bill_id': bill_id,
                    'customers': customers_with_discount,
                    'search_query': search_query
                })
            else:
                messages.error(request, "Please enter a name or phone number to search.")
        elif action == 'add_customer':
            name = request.POST.get('name')
            phone = request.POST.get('phone')
            if name and phone:
                try:
                    customer = Customer.objects.create(name=name, phone=phone, loyalty_points=0)
                    return redirect('final_bill', customer_id=customer.id)
                except:
                    messages.error(request, "Phone number already exists.")
            else:
                messages.error(request, "Both name and phone are required.")
        elif action == 'select_customer':
            customer_id = request.POST.get('customer_id')
            if customer_id:
                return redirect('final_bill', customer_id=customer_id)
            else:
                messages.error(request, "Please select a customer.")

    return render(request, 'customers/customer_entry.html', {'bill_id': bill_id})

@login_required
def final_bill(request, customer_id):
    bill_id = request.session.get('bill_id')
    if not bill_id:
        messages.error(request, "No bill in progress.")
        return redirect('create_bill')

    bill = get_object_or_404(Bill, id=bill_id)
    customer = get_object_or_404(Customer, id=customer_id)
    items = bill.items.all()
    total = sum(item.total_price for item in items)
    loyalty_discount = customer.loyalty_points // 10  # Compute discount in view
    final_amount = max(total - bill.discount - Decimal(loyalty_discount), 0)

    return render(request, 'billing/final_bill.html', {
        'bill': bill,
        'customer': customer,
        'items': items,
        'total': total,
        'discount': bill.discount + Decimal(loyalty_discount),
        'final_amount': final_amount,
        'loyalty_discount': loyalty_discount
    })

@login_required
def final_submit_bill(request, customer_id):
    bill_id = request.session.get('bill_id')
    if not bill_id:
        messages.error(request, "No bill in progress.")
        return redirect('create_bill')

    if request.method == 'POST':
        bill = get_object_or_404(Bill, id=bill_id)
        customer = get_object_or_404(Customer, id=customer_id)
        loyalty_discount = Decimal(request.POST.get('loyalty_discount', 0))

        # Update bill
        bill.customer = customer
        bill.total_amount = max(bill.total_amount - loyalty_discount, 0)
        bill.status = 'completed'
        bill.save()

        # Update inventory
        for item in bill.items.all():
            inventory = get_object_or_404(Inventory, product=item.product)
            inventory.quantity -= item.quantity
            inventory.save()

        # Update loyalty points
        earned_points = int(bill.total_amount // 100)  # ₹100 = 1 point
        spent_points = int(loyalty_discount * 10)  # ₹1 = 10 points
        customer.loyalty_points = max(customer.loyalty_points - spent_points, 0) + earned_points
        customer.save()

        # Clear session
        request.session.pop('bill_id', None)
        messages.success(request, f"Bill #{bill.bill_number} created successfully.")
        return redirect('bill_list')

    return redirect('final_bill', customer_id=customer_id)

@login_required
def bill_list(request):
    bills = Bill.objects.filter(status='completed')
    return render(request, 'billing/bill_list.html', {'bills': bills})

@login_required
def cashier_dashboard(request):
    return render(request, 'cashier_dashboard.html', {})

@login_required
def get_product_price(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return JsonResponse({'price': str(product.price)})