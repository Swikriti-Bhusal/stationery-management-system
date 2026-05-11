# from django.urls import path
# from . import views

# app_name = 'orders'   

# urlpatterns = [
#     path('place-order/', views.place_order, name='place_order'),
#     path('my-orders/', views.my_orders, name='my_orders'),
#     path('success/<int:order_id>/', views.order_success, name='order_success'),
#     path('detail/<int:order_id>/', views.order_detail, name='order_detail'),
# ]

from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Customer URLs
    path('place-order/', views.place_order, name='place_order'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('success/<int:order_id>/', views.order_success, name='order_success'),
    path('detail/<int:order_id>/', views.order_detail, name='order_detail'),
    
    # Admin URLs
    path('admin/orders/', views.admin_order_list, name='admin_order_list'),
    path('admin/orders/<int:order_id>/', views.admin_order_detail, name='admin_order_detail'),
    path('admin/orders/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
]