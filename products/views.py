from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, Category

# Customer Views
def product_list(request):
    products = Product.objects.filter(is_available=True)
    categories = Category.objects.all()
    return render(request, 'products/product_list.html', {
        'products': products,
        'categories': categories
    })

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'products/product_detail.html', {'product': product})

# Admin Views
@login_required
def admin_product_list(request):
    if request.user.role != 'admin':
        return redirect('customer_dashboard')
    
    products = Product.objects.all()
    return render(request, 'products/admin_product_list.html', {'products': products})