from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('place-order/', views.place_order, name='place_order'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('success/<int:order_id>/', views.order_success, name='order_success'),
]