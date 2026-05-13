
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from cart.models import Cart
from .models import Order, OrderItem


# ==================== CUSTOMER ORDER VIEWS ====================

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


@login_required
def my_orders(request):
    if request.user.role != 'customer':
        return redirect('admin_dashboard')
    
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    return render(request, 'orders/my_orders.html', {'orders': orders})


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_success.html', {'order': order})


@login_required
def order_detail(request, order_id):
    if request.user.role != 'customer':
        return redirect('admin_dashboard')
    
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = order.items.select_related('product').all()
    
    return render(request, 'orders/order_detail.html', {
        'order': order,
        'items': items
    })


# ==================== ADMIN ORDER VIEWS ====================

@login_required
def admin_order_list(request):
    if request.user.role != 'admin':
        return redirect('customer_dashboard')
    
    orders = Order.objects.all().order_by('-order_date')
    return render(request, 'orders/admin_order_list.html', {'orders': orders})


@login_required
def admin_order_detail(request, order_id):
    if request.user.role != 'admin':
        return redirect('customer_dashboard')
    
    order = get_object_or_404(Order, id=order_id)
    items = order.items.select_related('product').all()
    return render(request, 'orders/admin_order_detail.html', {
        'order': order,
        'items': items
    })


@login_required
def update_order_status(request, order_id):
    if request.user.role != 'admin':
        return redirect('customer_dashboard')
    
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        
        valid_statuses = ['pending', 'approved', 'shipped', 'delivered', 'cancelled']
        if new_status in valid_statuses:
            order.status = new_status
            order.save()
            messages.success(request, f"✅ Order #{order.id} status updated to {new_status.upper()} successfully!")
        else:
            messages.error(request, "Invalid status selected.")
    
    # Redirect back to the order list page
    return redirect('orders:admin_order_list')

