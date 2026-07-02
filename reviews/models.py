
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg, Count  # ADD THIS

class ProductRating(models.Model):
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['product', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.rating}★"
    
    
    @classmethod
    def get_weighted_rating(cls, product):
        """Calculate weighted rating for a product"""
        # Get all ratings for this product
        ratings = cls.objects.filter(product=product)
        count = ratings.count()
        
        # If no ratings, return 0
        if count == 0:
            return 0
        
        # Calculate average rating for this product
        avg = ratings.aggregate(Avg('rating'))['rating__avg'] or 0
        
        # Get global average across ALL products
        global_avg = cls.objects.aggregate(Avg('rating'))['rating__avg'] or 3.0
        
        # Minimum reviews required to be considered reliable
        min_reviews = 5
        
        # Weighted rating formula
        # (avg * count + global_avg * min_reviews) / (count + min_reviews)
        weighted = (avg * count + global_avg * min_reviews) / (count + min_reviews)
        
        return round(weighted, 1)