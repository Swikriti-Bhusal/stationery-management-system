from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from cart.models import Cart
from .models import Order, OrderItem

@login_required
def place_order(request):
    if request.user.role != 'customer':
        return redirect('admin_dashboard')
    
    cart = Cart.objects.filter(user=request.user).first()
    
    if not cart or not cart.items.exists():
        messages.error(request, "Your cart is empty!")
        return redirect('cart:cart_view')
    
    # Create new Order
    order = Order.objects.create(
        user=request.user,
        shipping_address=request.user.address or "No address provided",
        phone=request.user.phone or "Not provided",
        total_amount=0
    )
    
    total = 0
    for item in cart.items.all():
        if item.quantity > item.product.stock:
            messages.error(request, f"Not enough stock for {item.product.name}")
            order.delete()
            return redirect('cart:cart_view')
        
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price_at_time=item.product.price
        )
        total += item.product.price * item.quantity
        
        # Update Stock (Inventory Management)
        item.product.stock -= item.quantity
        item.product.save()
    
    order.total_amount = total
    order.save()
    
    # Clear the cart after order
    cart.items.all().delete()
    
    messages.success(request, f"Order #{order.id} placed successfully!")
    return redirect('orders:order_success', order_id=order.id)
    # return redirect('order_success', order_id=order.id)


@login_required
def my_orders(request):
    if request.user.role != 'customer':
        return redirect('admin_dashboard')
    
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    return render(request, 'orders/my_orders.html', {'orders': orders})


@login_required
def order_success(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    return render(request, 'orders/order_success.html', {'order': order})

