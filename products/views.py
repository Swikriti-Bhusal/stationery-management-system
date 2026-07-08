from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, Category
from reviews.models import ProductRating 
from django.db.models import Count, Q 

# ====================== LINEAR SEARCH ALGORITHM ======================
def linear_search_products(products, query):
    """Custom Linear Search Algorithm"""
    if not query:
        return products
    
    query = query.lower().strip()
    result = []
    
    for product in products:
        name = product.name.lower()
        desc = (product.description or "").lower()
        cat  = product.category.name.lower()
        
        # Whole word matching
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


# ====================== HELPER FUNCTION FOR RATINGS ======================
def add_ratings_to_products(products):
    """Add weighted rating and total ratings to each product"""
    for product in products:
        product.weighted_rating = ProductRating.get_weighted_rating(product)
        product.total_ratings = ProductRating.objects.filter(product=product).count()
    return products


# ====================== RECOMMENDATION FUNCTION ======================
def get_personalized_recommendations(user, limit=3):
    """Simple recommendations based on user's purchase history"""
    recommendations = []
    
    try:
        from orders.models import OrderItem
        
        # Get user's purchased product IDs
        purchased_product_ids = OrderItem.objects.filter(
            order__user=user
        ).values_list('product_id', flat=True)
        
        if purchased_product_ids:
            # Get categories from user's purchases
            purchased_categories = Product.objects.filter(
                id__in=purchased_product_ids
            ).values_list('category_id', flat=True).distinct()
            
            # Get products from same categories (excluding purchased)
            category_products = Product.objects.filter(
                category_id__in=purchased_categories,
                is_available=True
            ).exclude(
                id__in=purchased_product_ids
            ).annotate(
                purchase_count=Count('orderitem')
            ).order_by('-purchase_count')[:limit]
            
            # Add explanation and score
            for product in category_products:
                score = min(95, 40 + (product.purchase_count * 2))
                recommendations.append({
                    'product': product,
                    'explanation': 'Based on your favorite categories',
                    'score': score
                })
        
        # If not enough recommendations, add popular products
        if len(recommendations) < limit:
            remaining = limit - len(recommendations)
            popular = Product.objects.filter(
                is_available=True
            ).exclude(
                id__in=[r['product'].id for r in recommendations]
            ).annotate(
                order_count=Count('orderitem')
            ).filter(order_count__gt=0).order_by('-order_count')[:remaining]
            
            for product in popular:
                recommendations.append({
                    'product': product,
                    'explanation': 'Popular among customers',
                    'score': 75
                })
                
    except ImportError:
        # If OrderItem doesn't exist, show popular products
        popular = Product.objects.filter(
            is_available=True
        ).annotate(
            order_count=Count('orderitem')
        ).filter(order_count__gt=0).order_by('-order_count')[:limit]
        
        for product in popular:
            recommendations.append({
                'product': product,
                'explanation': 'Popular among customers',
                'score': 80
            })
    
    return recommendations


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
        products = list(products_qs)   

    # ========== ADD RATINGS TO PRODUCTS ==========
    products = add_ratings_to_products(products)
    
    # Sort by weighted rating if no search 
    if not search_query:
        products = sorted(products, key=lambda p: p.weighted_rating, reverse=True)
    
    # ========== GET RECOMMENDATIONS ==========
    hybrid_recommendations = []
    if request.user.is_authenticated:
        hybrid_recommendations = get_personalized_recommendations(request.user, limit=3)

    return render(request, 'products/product_list.html', {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'hybrid_recommendations': hybrid_recommendations
    })


# ====================== ADMIN VIEWS ======================
@login_required
def admin_product_list(request):
    if request.user.role != 'admin':
        return redirect('customer_dashboard')
    
    products = Product.objects.all().order_by('-id')
    return render(request, 'products/admin_product_list.html', {'products': products})