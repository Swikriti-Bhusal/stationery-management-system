
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Customer URLs
    path('checkout/', views.checkout, name='checkout'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('success/<int:order_id>/', views.order_success, name='order_success'),
    path('detail/<int:order_id>/', views.order_detail, name='order_detail'),
    
    # Khalti URLs
    path('khalti/initiate/<int:order_id>/', views.khalti_initiate, name='khalti_initiate'),
    # path('khalti/success/<int:order_id>/', views.khalti_success, name='khalti_success'),
    path('khalti/verify/', views.khalti_verify, name='khalti_verify'),
    
    
    # Admin URLs (these will be under /orders/admin/...)
    path('admin/orders/', views.admin_order_list, name='admin_order_list'),
    path('admin/orders/<int:order_id>/', views.admin_order_detail, name='admin_order_detail'),
    path('admin/orders/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
]



