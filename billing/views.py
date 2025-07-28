from django.shortcuts import render, redirect, get_object_or_404
from django.forms import formset_factory
from .models import Bill, BillItem
from .forms import BillForm, BillItemForm
from django.contrib.auth.decorators import login_required
from inventory.models import Inventory
from customers.models import Customer  # for check_customer
from django.contrib import messages
import uuid
from decimal import Decimal


@login_required
def create_bill(request):
    BillItemFormSet = formset_factory(BillItemForm, extra=1)

    if request.method == 'POST':
        bill_form = BillForm(request.POST)
        formset = BillItemFormSet(request.POST)
        action = request.POST.get('action')

        if action == 'check_customer':
            if bill_form.is_valid() and formset.is_valid():
                request.session['bill_data'] = {
                    'discount': float(bill_form.cleaned_data.get('discount', 0)),
                    'payment_method': bill_form.cleaned_data.get('payment_method')
                }
                request.session['bill_items'] = [
                    {
                        'product_id': form.cleaned_data['product'].id,
                        'quantity': form.cleaned_data['quantity']
                    }
                    for form in formset if form.cleaned_data
                ]
                return redirect('customer_entry')  # 👈 Go to customer entry form
            else:
                messages.error(request, "Please correct the form errors.")

    else:
        bill_form = BillForm()
        formset = BillItemFormSet()
        generated_bill_number = str(uuid.uuid4())[:8]

    return render(request, 'billing/bill_form.html', {
        'bill_form': bill_form,
        'formset': formset,
        'bill_number': locals().get('generated_bill_number')
    })



@login_required
def bill_list(request):
    bills = Bill.objects.all()
    return render(request, 'billing/bill_list.html', {'bills': bills})


@login_required
def check_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    bill_data = request.session.get('bill_data')
    bill_items = request.session.get('bill_items')

    if not bill_data or not bill_items:
        messages.error(request, "Bill session data missing. Please re-enter the bill.")
        return redirect('create_bill')

    # Loyalty calculation logic (example: ₹1 discount for every 10 points)
    loyalty_points = customer.loyalty_points
    discount_from_loyalty = loyalty_points // 10

    return render(request, 'billing/check_customer.html', {
        'customer': customer,
        'loyalty_points': loyalty_points,
        'discount_from_loyalty': discount_from_loyalty,
    })


from customers.models import Customer

from django.shortcuts import render, redirect, get_object_or_404
from .models import Customer

def customer_entry(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')

        if phone:
            try:
                # Try to find an existing customer by phone
                customer = Customer.objects.get(phone=phone)
                return redirect('customer_summary', customer_id=customer.id)
            except Customer.DoesNotExist:
                # If not found, create new customer if name is given
                if name:
                    customer = Customer.objects.create(name=name, phone=phone)
                    return redirect('customer_summary', customer_id=customer.id)
                else:
                    return render(request, 'billing/customer_entry.html', {
                        'error': "Customer not found. Please enter name to register."
                    })
    return render(request, 'billing/customer_entry.html')



from products.models import Product  # Adjust if needed

@login_required
def final_submit_bill(request, customer_id):
    if request.method == 'POST':
        bill_data = request.session.get('bill_data')
        bill_items = request.session.get('bill_items')
        loyalty_discount = float(request.POST.get('loyalty_discount', 0))

        if not bill_data or not bill_items:
            messages.error(request, "Session expired. Please start again.")
            return redirect('create_bill')

        customer = get_object_or_404(Customer, id=customer_id)

        # Create Bill
        bill = Bill.objects.create(
            bill_number=str(uuid.uuid4())[:8],
            cashier=request.user,
            customer=customer,
            discount=loyalty_discount,
            payment_method=bill_data.get('payment_method'),
            total_amount=0  # Will update later
        )

        total = 0
        for item in bill_items:
            product = get_object_or_404(Product, id=item['product_id'])
            quantity = item['quantity']
            price = product.price
            total += quantity * price

            # Inventory check
            inventory = Inventory.objects.get(product=product)
            if inventory.quantity < quantity:
                bill.delete()
                messages.error(request, f"Not enough stock for '{product.name}'.")
                return redirect('create_bill')

            inventory.quantity -= quantity
            inventory.save()

            BillItem.objects.create(
                bill=bill,
                product=product,
                quantity=quantity,
                price_at_purchase=price
            )

        # Apply discount
        loyalty_discount = float(request.POST.get('loyalty_discount', 0))
        loyalty_discount = Decimal(request.POST.get('loyalty_discount', '0'))
        bill.save()

        # Update loyalty points (earn 1 per ₹100 spent)
        earned_points = int(bill.total_amount // 100)
        spent_points = int(loyalty_discount * 10)
        customer.loyalty_points = customer.loyalty_points - spent_points + earned_points
        customer.save()

        # Clear session
        request.session.pop('bill_data', None)
        request.session.pop('bill_items', None)

        messages.success(request, f"Bill #{bill.bill_number} created successfully.")
        return redirect('final_bill', customer_id=customer.id)

    return redirect('final_bill')

def customer_summary(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    loyalty_points = customer.loyalty_points
    discount = loyalty_points * 1  # ₹1 per point

    if request.method == 'POST':
        # Logic to finalize and show bill
        bill = Bill.objects.filter(customer=customer).last()
        items = bill.items.all()
        total = sum(item.total_price for item in items)
        final_amount = total - discount

        return render(request, 'billing/final_bill.html', {
            'customer': customer,
            'bill': bill,
            'items': items,
            'total': total,
            'discount': discount,
            'final_amount': final_amount
        })

    return render(request, 'billing/customer_summary.html', {
        'customer': customer,
        'loyalty_points': loyalty_points,
        'discount': discount,
    })


from django.shortcuts import render, get_object_or_404
from .models import Customer, Bill

def final_bill(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    bill = Bill.objects.filter(customer=customer).last()
    items = bill.items.all()  # assuming a related_name='items' on BillItem model

    total = sum(item.total_price for item in items)
    discount = customer.loyalty_points * 1
    final_amount = total - discount

    return render(request, 'billing/final_bill.html', {
        'customer': customer,
        'bill': bill,
        'items': items,
        'total': total,
        'discount': discount,
        'final_amount': final_amount
    })
