from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import datetime, timedelta
import csv
import json
from users.decorators import role_required
from billing.models import Bill, BillItem
from inventory.models import Inventory
from products.models import Product

@method_decorator(login_required, name='dispatch')
@method_decorator(role_required('admin'), name='dispatch')
class ReportsDashboardView(TemplateView):
    template_name = 'reports/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get date range (last 30 days by default)
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
        
        # Sales data
        bills = Bill.objects.filter(
            created_at__range=[start_date, end_date],
            status='completed'
        )
        
        context['total_revenue'] = bills.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        context['total_bills'] = bills.count()
        context['total_discounts'] = bills.aggregate(Sum('discount'))['discount__sum'] or 0
        
        # Payment method breakdown
        payment_methods = bills.values('payment_method').annotate(
            count=Count('id'),
            total=Sum('total_amount')
        )
        context['payment_methods'] = payment_methods
        
        # Top selling products
        top_products = BillItem.objects.filter(
            bill__created_at__range=[start_date, end_date],
            bill__status='completed'
        ).values('product__name').annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('price_at_purchase')
        ).order_by('-total_quantity')[:10]
        
        context['top_products'] = top_products
        
        # Inventory alerts
        low_stock_items = Inventory.objects.filter(
            quantity__lt=F('restock_threshold')
        ).select_related('product')
        context['low_stock_items'] = low_stock_items
        
        return context

@method_decorator(login_required, name='dispatch')
@method_decorator(role_required('admin'), name='dispatch')
class SalesReportView(TemplateView):
    template_name = 'reports/sales.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get date range from request parameters
        period = self.request.GET.get('period', '30')
        end_date = timezone.now()
        start_date = end_date - timedelta(days=int(period))
        
        # Sales data
        bills = Bill.objects.filter(
            created_at__range=[start_date, end_date],
            status='completed'
        )
        
        # Daily sales data for chart
        daily_sales = bills.extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(
            total=Sum('total_amount'),
            count=Count('id')
        ).order_by('day')
        
        context['daily_sales'] = list(daily_sales)
        context['total_revenue'] = bills.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        context['total_bills'] = bills.count()
        context['average_bill'] = context['total_revenue'] / context['total_bills'] if context['total_bills'] > 0 else 0
        
        # Payment method breakdown
        payment_methods = bills.values('payment_method').annotate(
            count=Count('id'),
            total=Sum('total_amount')
        )
        
        # Calculate percentages
        for method in payment_methods:
            if context['total_revenue'] > 0:
                method['percentage'] = round((method['total'] / context['total_revenue']) * 100, 1)
            else:
                method['percentage'] = 0
        
        context['payment_methods'] = list(payment_methods)
        
        return context

@method_decorator(login_required, name='dispatch')
@method_decorator(role_required('admin'), name='dispatch')
class InventoryReportView(TemplateView):
    template_name = 'reports/inventory.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Current inventory status
        inventory_items = Inventory.objects.select_related('product').all()
        
        # Stock status breakdown
        total_items = inventory_items.count()
        low_stock_items = inventory_items.filter(
            quantity__lt=F('restock_threshold')
        ).count()
        out_of_stock_items = inventory_items.filter(quantity=0).count()
        
        context['total_items'] = total_items
        context['low_stock_items'] = low_stock_items
        context['out_of_stock_items'] = out_of_stock_items
        context['in_stock_items'] = total_items - low_stock_items - out_of_stock_items
        
        # Low stock items with calculated stock value
        low_stock_list = inventory_items.filter(
            quantity__lt=F('restock_threshold')
        )
        
        # Calculate stock value for each item
        for item in low_stock_list:
            item.stock_value = item.quantity * item.product.price
        
        context['low_stock_list'] = low_stock_list
        
        # Stock value
        total_value = sum(item.quantity * item.product.price for item in inventory_items)
        context['total_stock_value'] = total_value
        
        # Category breakdown
        category_data = {}
        for item in inventory_items:
            category = item.product.category.name
            if category not in category_data:
                category_data[category] = {'count': 0, 'value': 0}
            category_data[category]['count'] += 1
            category_data[category]['value'] += item.quantity * item.product.price
        
        # Calculate average value for each category
        for category, data in category_data.items():
            if data['count'] > 0:
                data['avg_value'] = data['value'] / data['count']
            else:
                data['avg_value'] = 0
        
        context['category_data'] = category_data
        
        return context

@login_required
@role_required('admin')
def export_sales_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Bill Number', 'Cashier', 'Total Amount', 'Discount', 'Payment Method', 'Customer'])
    
    # Get date range
    period = request.GET.get('period', '30')
    end_date = timezone.now()
    start_date = end_date - timedelta(days=int(period))
    
    bills = Bill.objects.filter(
        created_at__range=[start_date, end_date],
        status='completed'
    ).select_related('cashier', 'customer')
    
    for bill in bills:
        writer.writerow([
            bill.created_at.strftime('%Y-%m-%d %H:%M'),
            bill.bill_number,
            bill.cashier.username,
            bill.total_amount,
            bill.discount,
            bill.payment_method,
            bill.customer.name if bill.customer else 'Walk-in Customer'
        ])
    
    return response

@login_required
@role_required('admin')
def export_sales_pdf(request):
    # This would require a PDF library like reportlab or weasyprint
    # For now, return a simple response
    response = HttpResponse("PDF export functionality would be implemented here")
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'
    return response

@login_required
@role_required('admin')
def export_inventory_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="inventory_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Product', 'Category', 'Current Stock', 'Restock Threshold', 'Status', 'Last Restocked', 'Stock Value'])
    
    inventory_items = Inventory.objects.select_related('product__category').all()
    
    for item in inventory_items:
        status = 'Low Stock' if item.is_low_stock() else 'In Stock' if item.quantity > 0 else 'Out of Stock'
        stock_value = item.quantity * item.product.price
        
        writer.writerow([
            item.product.name,
            item.product.category.name,
            item.quantity,
            item.restock_threshold,
            status,
            item.last_restocked.strftime('%Y-%m-%d %H:%M'),
            stock_value
        ])
    
    return response

@login_required
@role_required('admin')
def export_inventory_pdf(request):
    # This would require a PDF library like reportlab or weasyprint
    # For now, return a simple response
    response = HttpResponse("PDF export functionality would be implemented here")
    response['Content-Disposition'] = 'attachment; filename="inventory_report.pdf"'
    return response
