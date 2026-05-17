from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from datetime import datetime, timedelta

from orders.models import Order, OrderItem
from products.models import Product


@login_required
def admin_reports(request):
    if request.user.role != 'admin':
        return redirect('customer_dashboard')

    # Total Sales & Orders
    total_sales = Order.objects.filter(
        status__in=['approved', 'delivered']
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    total_orders = Order.objects.count()

    # Best Selling Products with Current Stock
    best_selling = OrderItem.objects.values(
        'product__id', 'product__name', 'product__stock'
    ).annotate(total_sold=Sum('quantity')).order_by('-total_sold')[:10]

    # ==================== MOVING AVERAGE ALGORITHM ====================
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=90)   

    # Get daily sales
    daily_sales = Order.objects.filter(
        order_date__date__gte=start_date,
        status__in=['approved', 'delivered']
    ).values('order_date__date')\
     .annotate(daily_total=Sum('total_amount'))\
     .order_by('order_date__date')

    sales_list = [sale['daily_total'] or 0 for sale in daily_sales]

    # Moving Average Function
    def calculate_moving_average(data, window_size=30):
        if not data:
            return 0
        if len(data) < window_size:
            return round(sum(data) / len(data), 2)
        return round(sum(data[-window_size:]) / window_size, 2)

    ma_30day = calculate_moving_average(sales_list, 30)
    ma_60day = calculate_moving_average(sales_list, 60)

    context = {
        'total_sales': total_sales,
        'total_orders': total_orders,
        'best_selling': best_selling,
        'moving_average_30day': ma_30day,
        'moving_average_60day': ma_60day,
    }

    return render(request, 'reports/admin_reports.html', context)

# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# from django.db.models import Sum
# from datetime import datetime, timedelta

# from orders.models import Order, OrderItem


# @login_required
# def admin_reports(request):
#     if request.user.role != 'admin':
#         return redirect('customer_dashboard')

#     # Total Sales & Orders
#     total_sales = Order.objects.filter(
#         status__in=['approved', 'shipped', 'delivered']
#     ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0

#     total_orders = Order.objects.count()

#     # Best Selling Products 
#     best_selling = OrderItem.objects.values('product__name')\
#                     .annotate(total_sold=Sum('quantity'))\
#                     .order_by('-total_sold')[:10]

#     # ================== SIMPLE MOVING AVERAGE ==================
#     end_date = datetime.now().date()
#     start_date = end_date - timedelta(days=30)

#     # Get daily sales
#     daily_sales = Order.objects.filter(
#         order_date__date__gte=start_date,
#         order_date__date__lte=end_date,
#         status__in=['approved', 'shipped', 'delivered']
#     ).values('order_date__date')\
#      .annotate(daily_total=Sum('total_amount'))\
#      .order_by('order_date__date')

#     # Convert to simple list
#     sales_list = [sale['daily_total'] or 0 for sale in daily_sales]

#     # Simple Moving Average Function
#     def simple_moving_average(data, window=7):
#         if not data:
#             return 0
#         if len(data) < window:
#             return round(sum(data) / len(data), 2)
#         # Take last 'window' days average
#         return round(sum(data[-window:]) / window, 2)

#     ma_7day = simple_moving_average(sales_list, 7)
#     ma_30day = simple_moving_average(sales_list, 30)

#     context = {
#         'total_sales': total_sales,
#         'total_orders': total_orders,
#         'best_selling': best_selling,
#         'moving_average_7day': ma_7day,
#         'moving_average_30day': ma_30day,
#     }

#     return render(request, 'reports/admin_reports.html', context)