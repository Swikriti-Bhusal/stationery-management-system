from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from products.models import Product
from .models import Cart, CartItem

def get_user_cart(user):
    cart, created = Cart.objects.get_or_create(user=user)
    return cart


@login_required
def add_to_cart(request, product_id):
    if request.user.role != 'customer':
        messages.error(request, "Only customers can add items to cart.")
        return redirect('product_list')
    
    product = get_object_or_404(Product, id=product_id)
    
    if product.stock <= 0:
        messages.warning(request, f"{product.name} is out of stock!")
        return redirect('product_list')
    
    cart = get_user_cart(request.user)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, 
        product=product
    )
    
    if created:
        messages.success(request, f"{product.name} has been added to your cart.")
    else:
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f"Quantity of {product.name} increased (Now: {cart_item.quantity}).")
        else:
            messages.warning(request, "Not enough stock available!")
    
    return redirect('product_list')


@login_required
def cart_view(request):
    if request.user.role != 'customer':
        return redirect('admin_dashboard')
    
    cart = get_user_cart(request.user)
    cart_items = cart.items.select_related('product').all()   # Better query
    total_price = cart.get_total_price() if cart_items.exists() else 0
    
    return render(request, 'cart/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
    })

# Update Quantity (+ or -)
@login_required
def update_cart_quantity(request, item_id):
    if request.user.role != 'customer':
        return redirect('cart:cart_view')
    
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    action = request.GET.get('action')
    
    if action == 'increase':
        if cart_item.quantity < cart_item.product.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, "Quantity increased.")
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            messages.success(request, "Quantity decreased.")
        else:
            cart_item.delete()
            messages.success(request, "Item removed from cart.")
    
    return redirect('cart:cart_view')


# Remove Item from Cart
@login_required
def remove_from_cart(request, item_id):
    if request.user.role != 'customer':
        return redirect('cart:cart_view')
    
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect('cart:cart_view')