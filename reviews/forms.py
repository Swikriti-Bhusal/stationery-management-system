from django import forms
from .models import ProductRating

class RatingForm(forms.ModelForm):
    class Meta:
        model = ProductRating
        fields = ['rating', 'review']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, f'{i}★') for i in range(1, 6)]),
            'review': forms.Textarea(attrs={
                'rows': 4, 
                'placeholder': 'Write your review here...',
                'class': 'form-control'
            }),
        }
        labels = {
            'rating': 'Your Rating',
            'review': 'Your Review (optional)',
        }