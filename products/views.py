
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
        name = product.name.lower()
        desc = (product.description or "").lower()
        cat  = product.category.name.lower()
        
        # Whole word matching (better than simple 'in')
        import re
        word_pattern = r'\b' + re.escape(query) + r'\b'
        
        name_match = bool(re.search(word_pattern, name))
        desc_match = bool(re.search(word_pattern, desc))
        cat_match  = bool(re.search(word_pattern, cat))
        
        if name_match or cat_match or desc_match:
            # Priority: Name > Category > Description
            if name_match:
                score = 4
            elif cat_match:
                score = 3
            else:
                score = 1
                
            result.append((product, score))
    
    # Sort: Best matches first, then newest
    result.sort(key=lambda x: (x[1], x[0].id), reverse=True)
    
    return [item[0] for item in result]


# ====================== CUSTOMER VIEWS ======================
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'products/product_detail.html', {'product': product})


def product_list(request):
    products_qs = Product.objects.filter(is_available=True).select_related('category')
    categories = Category.objects.all()

    search_query = request.GET.get('q') or request.GET.get('search', '').strip()
    category_slug = request.GET.get('category')

    # Category Filter
    if category_slug:
        products_qs = products_qs.filter(category__slug=category_slug)

    # Apply Linear Search
    if search_query:
        products = linear_search_products(products_qs, search_query)
    else:
        products = list(products_qs)   # Convert to list

    # Sorting - Newest first when no search
    if not search_query:
        products = sorted(products, key=lambda p: p.id, reverse=True)

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

