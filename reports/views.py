from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from orders.models import Order, OrderItem
from products.models import Product
import pandas as pd
from datetime import datetime, timedelta

@login_required
def admin_reports(request):
    if request.user.role != 'admin':
        return redirect('customer_dashboard')

    # Total Sales
    total_sales = Order.objects.filter(status__in=['approved', 'shipped', 'delivered']).aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    # Total Orders
    total_orders = Order.objects.count()

    # Best Selling Products
    best_selling = OrderItem.objects.values('product__name')\
                    .annotate(total_sold=Sum('quantity'))\
                    .order_by('-total_sold')[:10]

    # Recent Orders (Last 7 days)
    recent_orders = Order.objects.filter(order_date__gte=datetime.now()-timedelta(days=7)).order_by('-order_date')[:10]

    context = {
        'total_sales': total_sales,
        'total_orders': total_orders,
        'best_selling': best_selling,
        'recent_orders': recent_orders,
    }

    return render(request, 'reports/admin_reports.html', context)