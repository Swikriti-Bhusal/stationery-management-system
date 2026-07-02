from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from products.models import Product
from .models import ProductRating

@login_required
def add_rating(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        rating_value = request.POST.get('rating')
        
        if rating_value:
            # Create or update rating
            rating, created = ProductRating.objects.update_or_create(
                product=product,
                user=request.user,
                defaults={'rating': rating_value}
            )
            
            if created:
                messages.success(request, 'Thank you for rating!')
            else:
                messages.success(request, 'Your rating has been updated!')
        
        return redirect(request.POST.get('next', 'product_list'))
    
    return render(request, 'reviews/rate_product.html', {'product': product})

@login_required
def delete_rating(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    rating = ProductRating.objects.filter(product=product, user=request.user).first()
    
    if rating:
        rating.delete()
        messages.success(request, 'Your rating has been removed.')
    
    return redirect(request.META.get('HTTP_REFERER', 'product_list'))

