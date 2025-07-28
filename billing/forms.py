from django import forms
from .models import Bill, BillItem
<<<<<<< HEAD
=======
from products.models import Product
from customers.models import Customer
>>>>>>> 207c8fcc7cd7ec2ff636bbe79f5a13da810261e0

class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ['discount', 'payment_method']
        widgets = {
            'discount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter flat discount like 10',
                'min': '0',
                'step': 'any',
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-control',
            }),
        }

class BillItemForm(forms.ModelForm):
    class Meta:
        model = BillItem
        fields = ['product', 'quantity']
        widgets = {
            'product': forms.Select(attrs={
                'class': 'form-control',
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
            }),
        }
