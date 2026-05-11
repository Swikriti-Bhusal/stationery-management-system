from django.urls import path
from . import views

urlpatterns = [
    # Customer URLs
    path('customer/register/', views.customer_register, name='customer_register'),
    path('customer/login/', views.customer_login, name='customer_login'),
    path('customer/logout/', views.customer_logout, name='customer_logout'),
    
    # Admin URLs
    path('admin/login/', views.admin_login, name='admin_login'),
    path('admin/logout/', views.admin_logout, name='admin_logout'),

        # Dashboard URLs
    path('customer/dashboard/', views.customer_dashboard, name='customer_dashboard'),
    # path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
path('staff/dashboard/', views.admin_dashboard, name='admin_dashboard'),

    path('', views.home, name='home'),
]