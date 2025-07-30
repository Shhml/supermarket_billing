from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path
from django.contrib import messages
from .views import export_sales_csv, export_inventory_csv

class ReportsAdmin(admin.ModelAdmin):
    """Admin interface for Reports functionality"""
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export-sales-csv/', self.admin_site.admin_view(self.export_sales_csv), name='export_sales_csv'),
            path('export-inventory-csv/', self.admin_site.admin_view(self.export_inventory_csv), name='export_inventory_csv'),
        ]
        return custom_urls + urls
    
    def export_sales_csv(self, request):
        """Admin action to export sales CSV"""
        try:
            response = export_sales_csv(request)
            messages.success(request, 'Sales report exported successfully!')
            return response
        except Exception as e:
            messages.error(request, f'Error exporting sales report: {str(e)}')
            return HttpResponseRedirect('../')
    
    def export_inventory_csv(self, request):
        """Admin action to export inventory CSV"""
        try:
            response = export_inventory_csv(request)
            messages.success(request, 'Inventory report exported successfully!')
            return response
        except Exception as e:
            messages.error(request, f'Error exporting inventory report: {str(e)}')
            return HttpResponseRedirect('../')
    
    def changelist_view(self, request, extra_context=None):
        """Custom changelist view for reports admin"""
        extra_context = extra_context or {}
        extra_context.update({
            'title': 'Reports Management',
            'reports_available': True,
        })
        return super().changelist_view(request, extra_context)
