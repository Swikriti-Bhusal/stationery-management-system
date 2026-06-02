from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
import requests

from cart.models import Cart
from .models import Order, OrderItem, Payment


# ==================== CHECKOUT ====================
@login_required
def checkout(request):
    if request.user.role != 'customer':
        return redirect('customer_dashboard')
    
    cart = Cart.objects.filter(user=request.user).first()
    
    if not cart or not cart.items.exists():
        messages.error(request, "Your cart is empty!")
        return redirect('cart:cart_view')

    if request.method == 'POST':
        shipping_address = request.POST.get('shipping_address')
        phone = request.POST.get('phone')
        payment_method = request.POST.get('payment_method')

        if not all([shipping_address, phone]):
            messages.error(request, "Shipping address and phone number are required!")
            return redirect('orders:checkout')

        full_name = request.user.get_full_name() or request.user.username or "Customer"

        # Create Order
        order = Order.objects.create(
            user=request.user,
            full_name=full_name,
            shipping_address=shipping_address,
            phone=phone,
            total_amount=0,
            status='pending'
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

            # Reduce stock immediately
            item.product.stock -= item.quantity
            item.product.save()

        order.total_amount = total
        order.save()

        # === IMPORTANT: Do NOT clear cart here for Khalti ===
        if payment_method == 'khalti':
            return redirect('orders:khalti_initiate', order_id=order.id)
        else:
            # For Cash on Delivery - clear cart and create payment
            cart.items.all().delete()
            
            Payment.objects.create(
                order=order,
                payment_method='cod',
                payment_status='completed',
                amount=total
            )
            messages.success(request, f"Order #{order.id} placed successfully! Pay on delivery.")
            return redirect('orders:order_success', order_id=order.id)

    return render(request, 'orders/checkout.html', {'cart': cart})


# ==================== KHALTI PAYMENT INITIATION ====================
@login_required
def khalti_initiate(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if Payment.objects.filter(order=order).exists():
        messages.warning(request, "Payment already initiated for this order.")
        return redirect('orders:order_success', order_id=order.id)

    khalti_secret_key = getattr(settings, 'KHALTI_SECRET_KEY', None)
    if not khalti_secret_key:
        messages.error(request, "Khalti payment is not configured properly.")
        return redirect('orders:checkout')

    customer_name = str(order.full_name or request.user.get_full_name() or request.user.username or "Customer").strip()
    customer_email = request.user.email or "noemail@example.com"
    customer_phone = order.phone or "9800000000"

    payload = {
        "return_url": request.build_absolute_uri(reverse('orders:khalti_verify')),
        "website_url": request.build_absolute_uri('/'),
        "amount": int(order.total_amount * 100),   # in paisa
        "purchase_order_id": str(order.id),
        "purchase_order_name": f"Order #{order.id}",
        "customer_info": {
            "name": customer_name,
            "email": customer_email,
            "phone": customer_phone,
        }
    }

    headers = {
        "Authorization": f"Key {khalti_secret_key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            "https://a.khalti.com/api/v2/epayment/initiate/",
            json=payload,
            headers=headers,
            timeout=15
        )
        
        print("=== KHALTI RESPONSE ===")
        print(f"Status Code: {response.status_code}")
        print(response.text)

        if response.status_code == 200:
            data = response.json()
            if data.get('payment_url'):
                Payment.objects.create(
                    order=order,
                    payment_method='khalti',
                    payment_status='pending',
                    amount=order.total_amount,
                    khalti_pidx=data.get('pidx')
                )
                return redirect(data['payment_url'])
            else:
                messages.error(request, "Invalid response from Khalti.")
        else:
            error_detail = response.json().get('detail', response.text[:300])
            messages.error(request, f"Khalti Error: {error_detail}")

    except requests.exceptions.RequestException as e:
        messages.error(request, f"Network error: Could not connect to Khalti.")
    except Exception as e:
        messages.error(request, f"Payment initiation failed: {str(e)}")

    return redirect('orders:checkout')


# ==================== KHALTI PAYMENT VERIFICATION ====================
@login_required
def khalti_verify(request):
    """Verify Khalti payment after user returns from Khalti"""
    
    pidx = request.GET.get('pidx')
    transaction_id = request.GET.get('transaction_id')
    
    if not pidx:
        messages.error(request, "No payment information received.")
        return redirect('cart:cart_view')
    
    try:
        payment = Payment.objects.get(khalti_pidx=pidx)
        order = payment.order
        
        # Verify with Khalti
        khalti_url = "https://a.khalti.com/api/v2/epayment/lookup/"
        headers = {
            "Authorization": f"Key {settings.KHALTI_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        
        response = requests.post(khalti_url, json={"pidx": pidx}, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            status = data.get('status')
            
            if status == 'Completed':
                payment.payment_status = 'completed'
                payment.khalti_transaction_id = transaction_id or data.get('transaction_id')
                payment.save()

                order.status = 'paid'          # Changed to 'paid' (better than 'delivered')
                order.save()

                # === Clear cart only after successful payment ===
                Cart.objects.filter(user=request.user).delete()

                messages.success(request, f"✅ Payment Successful! Order #{order.id} has been confirmed.")
                return redirect('orders:order_success', order_id=order.id)
            else:
                payment.payment_status = 'failed'
                payment.save()
                
                messages.error(request, f"Payment {status}. Please try again.")
                return redirect('orders:checkout')
        else:
            messages.error(request, "Could not verify payment with Khalti.")
            return redirect('orders:checkout')
            
    except Payment.DoesNotExist:
        messages.error(request, "Payment record not found.")
        return redirect('cart:cart_view')
    except Exception as e:
        messages.error(request, f"Verification error: {str(e)}")
        return redirect('orders:checkout')


# ==================== CUSTOMER ORDERS ====================
@login_required
def my_orders(request):
    if request.user.role != 'customer':
        return redirect('admin_dashboard')
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    return render(request, 'orders/my_orders.html', {'orders': orders})


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Get payment info
    try:
        payment = Payment.objects.get(order=order)
    except Payment.DoesNotExist:
        payment = None
    
    return render(request, 'orders/order_success.html', {
        'order': order,
        'payment': payment
    })


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    # Check if user is admin or order owner
    if request.user.role != 'admin' and order.user != request.user:
        return redirect('customer_dashboard')
    
    try:
        payment = Payment.objects.get(order=order)
    except Payment.DoesNotExist:
        payment = None
        
    return render(request, 'orders/order_detail.html', {
        'order': order,
        'payment': payment
    })


# ==================== ADMIN ORDERS ====================
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
    
    try:
        payment = Payment.objects.get(order=order)
    except Payment.DoesNotExist:
        payment = None
        
    return render(request, 'orders/admin_order_detail.html', {
        'order': order,
        'payment': payment
    })


@login_required
def update_order_status(request, order_id):
    if request.user.role != 'admin':
        return redirect('customer_dashboard')
    
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        
        # Only allow pending, delivered, cancelled
        if new_status in ['pending', 'delivered', 'cancelled']:
            order.status = new_status
            order.save()
            messages.success(request, f"Order #{order.id} status updated to {new_status.upper()}!")
        else:
            messages.error(request, "Invalid status selected")
    
    return redirect('orders:admin_order_list')



