from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product
from customers.models import Customer

User = get_user_model()

class Bill(models.Model):
    bill_number = models.CharField(max_length=20, unique=True)
    cashier = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=20, choices=[
        ('Cash', 'Cash'),
        ('Card', 'Card'),
        ('UPI', 'UPI')
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, default='draft', choices=[('draft', 'Draft'), ('completed', 'Completed')])

    def __str__(self):
        return f"Bill #{self.bill_number}"

class BillItem(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def total_price(self):
        return self.quantity * self.price_at_purchase

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"