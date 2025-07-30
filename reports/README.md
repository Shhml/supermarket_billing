# Reports App

The Reports app provides comprehensive analytical reports for the Supermarket Billing System, offering insights into sales, inventory, and product performance.

## Features

### 1. Reports Dashboard (`/reports/`)
- **Overview Statistics**: Total revenue, bills, discounts, and low stock alerts
- **Interactive Charts**: Payment methods breakdown and top-selling products
- **Low Stock Alerts**: Real-time alerts for items requiring restocking
- **Export Options**: Quick access to CSV and PDF exports

### 2. Sales Reports (`/reports/sales/`)
- **Period Selection**: Filter data by 7, 30, 90 days or 1 year
- **Sales Analytics**: Total revenue, bill count, and average bill amount
- **Visual Charts**: Daily sales trends and payment method distribution
- **Detailed Tables**: Payment method breakdown with percentages

### 3. Inventory Reports (`/reports/inventory/`)
- **Stock Status**: Overview of in-stock, low-stock, and out-of-stock items
- **Category Analysis**: Distribution and value by product category
- **Low Stock Management**: Detailed list of items requiring attention
- **Stock Valuation**: Total inventory value and per-category breakdown

## Access Control

- **Admin Only**: All reports are restricted to users with admin role
- **Secure Access**: Uses `@role_required('admin')` decorator
- **Login Required**: All views require user authentication

## Export Functionality

### CSV Exports
- **Sales CSV**: Date, bill number, cashier, amount, discount, payment method, customer
- **Inventory CSV**: Product, category, stock levels, thresholds, status, last restocked, value

### PDF Exports
- **Placeholder Implementation**: Ready for PDF library integration
- **Future Enhancement**: Will support full PDF report generation

## Technical Implementation

### Views
- `ReportsDashboardView`: Main dashboard with summary statistics
- `SalesReportView`: Detailed sales analysis with period filtering
- `InventoryReportView`: Comprehensive inventory status and analysis
- Export functions: `export_sales_csv`, `export_sales_pdf`, `export_inventory_csv`, `export_inventory_pdf`

### Templates
- `dashboard.html`: Main reports dashboard
- `sales.html`: Sales report with charts and period selection
- `inventory.html`: Inventory report with status overview

### Charts
- **Chart.js Integration**: Interactive charts for data visualization
- **Responsive Design**: Charts adapt to different screen sizes
- **Multiple Chart Types**: Pie charts, bar charts, line charts, doughnut charts

## Data Sources

The reports app aggregates data from:
- **Billing App**: Bill and BillItem models for sales data
- **Inventory App**: Inventory model for stock information
- **Products App**: Product and Category models for product details
- **Customers App**: Customer model for customer information

## Future Enhancements

1. **Real-time Updates**: WebSocket integration for live data updates
2. **Custom Date Ranges**: User-defined date range selection
3. **Advanced Visualizations**: Additional chart types and interactive features
4. **Customer Reports**: Customer-specific analytics and insights
5. **PDF Generation**: Full PDF report implementation with styling
6. **Email Reports**: Automated report delivery via email
7. **Report Scheduling**: Automated report generation at specified intervals

## Usage

1. **Access Reports**: Navigate to `/reports/` from admin dashboard
2. **View Dashboard**: See overview statistics and charts
3. **Generate Reports**: Use period selectors and export buttons
4. **Download Data**: Export reports in CSV or PDF format
5. **Monitor Alerts**: Check low stock alerts for inventory management

## Dependencies

- Django 4.2+
- Chart.js 3.7.0 (CDN)
- Bootstrap 5.3.0 (for styling)
- mathfilters (for template calculations)

## Security

- Role-based access control
- Admin-only permissions
- Secure data aggregation
- No sensitive data exposure in exports 