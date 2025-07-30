from django import forms
from .models import Customer

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'email', 'address', 'loyalty_points']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter customer name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter address'}),
            'loyalty_points': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and len(phone) < 10:
            raise forms.ValidationError("Phone number must be at least 10 digits long.")
        return phone
