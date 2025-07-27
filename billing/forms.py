from django import forms
from .models import Bill, BillItem
from products.models import Product
from customers.models import Customer

class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ['discount', 'payment_method']

class BillItemForm(forms.ModelForm):
    class Meta:
        model = BillItem
        fields = ['product', 'quantity']
