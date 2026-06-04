from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from products.models import Category, Product
from .forms import CustomerRegistrationForm
from .models import CustomUser
from django.db.models import Sum, Q
from orders.models import Order

# Customer Registration
def customer_register(request):
    if request.user.is_authenticated:
        return redirect('product_list')
    
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('product_list')
    else:
        form = CustomerRegistrationForm()
    
    return render(request, 'accounts/customer_register.html', {'form': form})


# Customer Login
def customer_login(request):
    # Clear messages when loading login page
    if request.method == 'GET':
        storage = messages.get_messages(request)
        for _ in storage:
            pass
    
    if request.user.is_authenticated:
        if request.user.role == 'admin':
            return redirect('admin_dashboard')
        return redirect('product_list')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            if user.role == 'admin':
                login(request, user)
                return redirect('admin_dashboard')
            else:
                login(request, user)
                return redirect('product_list')
        else:
            messages.error(request, "Invalid email or password. Please try again.")
    
    return render(request, 'accounts/customer_login.html')


# Admin Login
def admin_login(request):
    # Clear messages when loading admin login page
    if request.method == 'GET':
        storage = messages.get_messages(request)
        for _ in storage:
            pass
    
    if request.user.is_authenticated:
        if request.user.role == 'admin':
            return redirect('admin_dashboard')
        else:
            return redirect('product_list')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None and user.role == 'admin':
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Invalid admin credentials. Please use admin account only.")
    
    return render(request, 'accounts/admin_login.html')


# Logout
def customer_logout(request):
    # Clear messages before logout
    storage = messages.get_messages(request)
    for _ in storage:
        pass
    logout(request)
    return redirect('home')


def admin_logout(request):
    # Clear messages before logout
    storage = messages.get_messages(request)
    for _ in storage:
        pass
    logout(request)
    return redirect('home')


# Dashboards 
@login_required
def customer_dashboard(request):
    if request.user.role != 'customer':
        return redirect('admin_dashboard')
    return render(request, 'accounts/customer_dashboard.html', {'user': request.user})


def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')


@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        return redirect('customer_dashboard')

    total_orders = Order.objects.count()
    
    total_revenue = Order.objects.filter(
        status__in=['approved', 'delivered']
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    pending_orders = Order.objects.filter(status='pending').count()
    low_stock = Product.objects.filter(stock__lte=10).count()
    total_products = Product.objects.count()

    context = {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'pending_orders': pending_orders,
        'low_stock': low_stock,
        'total_products': total_products,
    }
    
    return render(request, 'accounts/admin_dashboard.html', context)


# ==================== USER MANAGEMENT  ====================

@login_required
def admin_user_list(request):
    """View all users (Admin only)"""
    if request.user.role != 'admin':
        return redirect('customer_dashboard')
    
    # Get all users except the current admin
    users = CustomUser.objects.all().order_by('-date_joined')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(
            Q(email__icontains=search_query) | 
            Q(full_name__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    # Get order count for each user
    for user in users:
        user.order_count = Order.objects.filter(user=user).count()
    
    return render(request, 'accounts/admin_user_list.html', {
        'users': users,
        'search_query': search_query
    })


@login_required
def admin_user_detail(request, user_id):
    """View user details and order history (Admin only)"""
    if request.user.role != 'admin':
        return redirect('customer_dashboard')
    
    user = get_object_or_404(CustomUser, id=user_id)
    orders = Order.objects.filter(user=user).order_by('-order_date')
    
    total_spent = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    return render(request, 'accounts/admin_user_detail.html', {
        'user': user,
        'orders': orders,
        'order_count': orders.count(),
        'total_spent': total_spent
    })


@login_required
def admin_user_delete(request, user_id):
    """Delete a user (Admin only)"""
    if request.user.role != 'admin':
        return redirect('customer_dashboard')
    
    user_to_delete = get_object_or_404(CustomUser, id=user_id)
    
    # Prevent admin from deleting themselves
    if user_to_delete.id == request.user.id:
        messages.error(request, "You cannot delete your own account.")
        return redirect('admin_user_list')
    
    user_name = user_to_delete.full_name or user_to_delete.email
    user_to_delete.delete()
    messages.success(request, f"User '{user_name}' has been deleted successfully.")
    
    return redirect('admin_user_list')


# def home(request):
#     products = Product.objects.filter(is_available=True)[:8]
#     categories = Category.objects.all()
#     return render(request, 'home.html', {
#         'products': products,
#         'categories': categories
#     })




def home(request):
    """Home page - shows static content for guests, dynamic for logged-in users"""
    if request.user.is_authenticated:
        # Logged-in users get dynamic content from database
        products = Product.objects.filter(is_available=True)[:8]
        categories = Category.objects.all()
        return render(request, 'home.html', {
            'products': products,
            'categories': categories
        })
    else:
        # Guests get static page
        return render(request, 'guest_home.html')    