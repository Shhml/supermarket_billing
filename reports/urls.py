from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.ReportsDashboardView.as_view(), name='dashboard'),
    path('sales/', views.SalesReportView.as_view(), name='sales'),
    path('inventory/', views.InventoryReportView.as_view(), name='inventory'),
    path('export/sales/csv/', views.export_sales_csv, name='export_sales_csv'),
    path('export/sales/pdf/', views.export_sales_pdf, name='export_sales_pdf'),
    path('export/inventory/csv/', views.export_inventory_csv, name='export_inventory_csv'),
    path('export/inventory/pdf/', views.export_inventory_pdf, name='export_inventory_pdf'),
] 