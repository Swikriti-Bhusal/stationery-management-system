# orders/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.conf import settings
from .models import Order, OrderItem, Payment
from cart.models import Cart  # adjust based on your cart model
import requests
import json

@login_required
def checkout(request):
    # Get user's cart
    cart = Cart.objects.filter(user=request.user, is_active=True).first()
    
    if not cart or cart.items.count() == 0:
        return redirect('cart:cart_detail')
    
    # Pre-fill user info for the form
    user = request.user
    initial_data = {
        'full_name': user.get_full_name() or user.username,
        'phone': getattr(user, 'phone', '') or user.contact_number if hasattr(user, 'contact_number') else '',
        'shipping_address': getattr(user, 'address', '') or '',
    }
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        shipping_address = request.POST.get('shipping_address')
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            full_name=full_name,
            phone=phone,
            shipping_address=shipping_address,
            total_amount=cart.total_price(),
            status='pending'
        )
        
        # Copy cart items to order items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price_at_time=cart_item.product.price
            )
        
        # Create payment record
        payment = Payment.objects.create(
            order=order,
            payment_method=payment_method,
            payment_status='pending',
            amount=order.total_amount
        )
        
        # Clear the cart
        cart.is_active = False
        cart.save()
        
        if payment_method == 'cod':
            # Cash on Delivery - order confirmed immediately
            payment.payment_status = 'completed'
            payment.save()
            order.status = 'confirmed'
            order.save()
            return redirect('orders:order_success', order_id=order.id)
        
        else:  # Khalti payment
            return redirect('orders:initiate_khalti', order_id=order.id)
    
    # GET request - show checkout form
    return render(request, 'orders/checkout.html', {
        'cart': cart,
        'total': cart.total_price(),
        'initial_data': initial_data,
    })