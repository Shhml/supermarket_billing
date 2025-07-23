from django.shortcuts import render, redirect
from django.forms import formset_factory
from .models import Bill, BillItem
from .forms import BillForm, BillItemForm
from django.contrib.auth.decorators import login_required
from inventory.models import Inventory
from django.contrib import messages
import uuid

@login_required
def create_bill(request):
    BillItemFormSet = formset_factory(BillItemForm, extra=1)  # Start with 1 product form

    if request.method == 'POST':
        bill_form = BillForm(request.POST)
        formset = BillItemFormSet(request.POST)

        if bill_form.is_valid() and formset.is_valid():
            bill = bill_form.save(commit=False)
            bill.bill_number = str(uuid.uuid4())[:8]  # Auto generate
            bill.cashier = request.user
            bill.total_amount = 0
            bill.save()

            total = 0
            for form in formset:
                if form.cleaned_data:
                    item = form.save(commit=False)
                    item.bill = bill
                    item.price_at_purchase = item.product.price
                    total += item.quantity * item.price_at_purchase

                    try:
                        inventory = Inventory.objects.get(product=item.product)
                        if inventory.quantity < item.quantity:
                            bill.delete()
                            return render(request, 'billing/bill_form.html', {
                                'bill_form': bill_form,
                                'formset': formset,
                                'bill_number': bill.bill_number,
                                'error': f"Insufficient stock for '{item.product.name}'"
                            })

                        inventory.quantity -= item.quantity
                        inventory.save()
                        item.save()
                    except Inventory.DoesNotExist:
                        bill.delete()
                        return render(request, 'billing/bill_form.html', {
                            'bill_form': bill_form,
                            'formset': formset,
                            'bill_number': bill.bill_number,
                            'error': f"Inventory not found for product: {item.product.name}"
                        })

            total -= bill.discount
            bill.total_amount = max(total, 0)
            bill.save()

            messages.success(request, f"Bill #{bill.bill_number} created successfully!")
            return redirect('bill_list')
    else:
        bill_form = BillForm()
        formset = BillItemFormSet()
        generated_bill_number = str(uuid.uuid4())[:8]  # Pre-generate for display

    return render(request, 'billing/bill_form.html', {
        'bill_form': bill_form,
        'formset': formset,
        'bill_number': locals().get('generated_bill_number')  # use only in GET
    })

@login_required
def bill_list(request):
    bills = Bill.objects.all()
    return render(request, 'billing/bill_list.html', {'bills': bills})
