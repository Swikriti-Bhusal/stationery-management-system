from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, Category


# ====================== LINEAR SEARCH ALGORITHM ======================
def linear_search_products(products, query):
    """Custom Linear Search Algorithm as per syllabus requirement"""
    if not query:
        return products
    
    query = query.lower().strip()
    result = []
    
    for product in products:
        if (query in product.name.lower() or 
            query in (product.description or "").lower() or 
            query in product.category.name.lower()):
            result.append(product)
    
    return result


# ====================== CUSTOMER VIEWS ======================
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'products/product_detail.html', {'product': product})


def product_list(request):
    # Start with QuerySet
    products_qs = Product.objects.filter(is_available=True).select_related('category')
    categories = Category.objects.all()

    search_query = request.GET.get('q') or request.GET.get('search', '').strip()
    category_slug = request.GET.get('category')

    # Category Filter
    if category_slug:
        products_qs = products_qs.filter(category__slug=category_slug)

    # Apply Linear Search Algorithm
    if search_query:
        products = linear_search_products(products_qs, search_query)
    else:
        products = products_qs

    # Sorting - Newest first
    if isinstance(products, list):
        products = sorted(products, key=lambda p: p.id, reverse=True)
    else:
        products = products.order_by('-id')

    return render(request, 'products/product_list.html', {
        'products': products,
        'categories': categories,
        'search_query': search_query
    })


# ====================== ADMIN VIEWS ======================
@login_required
def admin_product_list(request):
    if request.user.role != 'admin':
        return redirect('customer_dashboard')
    
    products = Product.objects.all().order_by('-id')
    return render(request, 'products/admin_product_list.html', {'products': products})



