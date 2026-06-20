from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('rate/<int:product_id>/', views.add_rating, name='add_rating'),
    path('delete/<int:product_id>/', views.delete_rating, name='delete_rating'),
]