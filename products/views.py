from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Product, Category

# Customer Views
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'products/product_detail.html', {'product': product})

def product_list(request):
    # Start with all available products
    products = Product.objects.filter(is_available=True)
    categories = Category.objects.all()
    
    # Get search query from URL
    search_query = request.GET.get('q') or request.GET.get('search', '')
    
    # Apply search if query exists - Search in name, description, and category name
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    # Category filter
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    # Order products by newest first (optional)
    products = products.order_by('-id')
    
    return render(request, 'products/product_list.html', {
        'products': products,
        'categories': categories,
        'search_query': search_query
    })

# Admin Views
@login_required
def admin_product_list(request):
    if request.user.role != 'admin':
        return redirect('customer_dashboard')
    
    products = Product.objects.all().order_by('-id')
    return render(request, 'products/admin_product_list.html', {'products': products})
#  from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required
# from .models import Product, Category

# # Customer Views
# def product_detail(request, slug):
#     product = get_object_or_404(Product, slug=slug)
#     return render(request, 'products/product_detail.html', {'product': product})

# def product_list(request):
#     products = Product.objects.filter(is_available=True)
#     categories = Category.objects.all()

#     # Search functionality
#     search_query = request.GET.get('search')
#     if search_query:
#         products = products.filter(name__icontains=search_query)

#     # Category filter
#     category_slug = request.GET.get('category')
#     if category_slug:
#         products = products.filter(category__slug=category_slug)

#     return render(request, 'products/product_list.html', {
#         'products': products,
#         'categories': categories,
#         'search_query': search_query
#     })

# # Admin Views
# @login_required
# def admin_product_list(request):
#     if request.user.role != 'admin':
#         return redirect('customer_dashboard')
    
#     products = Product.objects.all()
#     return render(request, 'products/admin_product_list.html', {'products': products})