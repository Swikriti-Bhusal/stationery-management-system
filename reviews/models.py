from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

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