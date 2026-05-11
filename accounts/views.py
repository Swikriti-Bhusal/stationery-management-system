from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from products.models import Category, Product
from .forms import CustomerRegistrationForm
from .models import CustomUser

# Customer Registration
def customer_register(request):
    if request.user.is_authenticated:
        return redirect('customer_dashboard')
    
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('customer_dashboard')
    else:
        form = CustomerRegistrationForm()
    
    return render(request, 'accounts/customer_register.html', {'form': form})


# Customer Login - FIXED
def customer_login(request):
    if request.user.is_authenticated:
        if request.user.role == 'admin':
            return redirect('admin_dashboard')
        return redirect('customer_dashboard')
    
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
                return redirect('customer_dashboard')
        else:
            messages.error(request, "Invalid email or password. Please try again.")
    
    return render(request, 'accounts/customer_login.html')

# Admin Login - IMPROVED
# def admin_login(request):
#     if request.user.is_authenticated:
#         if request.user.role == 'admin':
#             return redirect('admin_dashboard')
#         return redirect('customer_dashboard')
    
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         password = request.POST.get('password')
        
#         user = authenticate(request, username=email, password=password)
        
#         if user is not None and user.role == 'admin':
#             login(request, user)
#             messages.success(request, "Welcome Admin!")
#             return redirect('admin_dashboard')
#         else:
#             messages.error(request, "Invalid admin credentials or you are not an admin.")
    
#     return render(request, 'accounts/admin_login.html')
def admin_login(request):
    if request.user.is_authenticated:
        if request.user.role == 'admin':
            return redirect('admin_dashboard')
        else:
            return redirect('customer_dashboard')
    
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

# Temporary Dashboards
@login_required
def customer_dashboard(request):
    if request.user.role != 'customer':
        return redirect('admin_dashboard')
    return render(request, 'accounts/customer_dashboard.html', {'user': request.user})

@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        return redirect('customer_dashboard')
    return render(request, 'accounts/admin_dashboard.html', {'user': request.user})


def home(request):
    products = Product.objects.filter(is_available=True)[:8]  # Show 8 featured products
    categories = Category.objects.all()
    return render(request, 'home.html', {
        'products': products,
        'categories': categories
    })


