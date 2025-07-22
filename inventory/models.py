from django.db import models
from products.models import Product
from django.utils import timezone

class Inventory(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    restock_threshold = models.PositiveIntegerField()
    last_restocked = models.DateTimeField(default=timezone.now)

    def is_low_stock(self):
        return self.quantity < self.restock_threshold

    def __str__(self):
        return f"{self.product.name} - {self.quantity} in stock"
