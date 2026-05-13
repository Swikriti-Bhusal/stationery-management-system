from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from products.models import Category, Product
from .forms import CustomerRegistrationForm
from .models import CustomUser
from django.db.models import Sum
from orders.models import Order  # Make sure this import exists

# Customer Registration
def customer_register(request):
    if request.user.is_authenticated:
        return redirect('product_list')  # Changed from customer_dashboard to product_list
    
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('product_list')  # Changed from customer_dashboard to product_list
    else:
        form = CustomerRegistrationForm()
    
    return render(request, 'accounts/customer_register.html', {'form': form})


# Customer Login - UPDATED (redirects to products page)
def customer_login(request):
    if request.user.is_authenticated:
        if request.user.role == 'admin':
            return redirect('admin_dashboard')
        return redirect('product_list')  # Changed from customer_dashboard to product_list
    
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
                messages.success(request, f"Welcome back, {user.full_name}!")
                return redirect('product_list')  # Changed from customer_dashboard to product_list
        else:
            messages.error(request, "Invalid email or password. Please try again.")
    
    return render(request, 'accounts/customer_login.html')

def admin_login(request):
    if request.user.is_authenticated:
        if request.user.role == 'admin':
            return redirect('admin_dashboard')
        else:
            return redirect('product_list')  # Changed from customer_dashboard to product_list
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None and user.role == 'admin':
            login(request, user)
            messages.success(request, f"Welcome Admin, {user.full_name}!")
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Invalid admin credentials. Please use admin account only.")
    
    return render(request, 'accounts/admin_login.html')

# Logout
def customer_logout(request):
    logout(request)
    return redirect('customer_login')

def admin_logout(request):
    logout(request)
    return redirect('admin_login')

# Temporary Dashboards (keeping but not redirecting to it automatically)
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
    
    # Revenue from ALL completed orders (COD + Online)
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
    
    return render(request, 'accounts/admin_dashboard.html', context)  # Fixed this line

def home(request):
    products = Product.objects.filter(is_available=True)[:8]
    categories = Category.objects.all()
    return render(request, 'home.html', {
        'products': products,
        'categories': categories
    })