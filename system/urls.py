from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Customer URLs (No /admin/ prefix)
    path('', include('accounts.urls')),
    path('products/', include('products.urls')),
    path('cart/', include('cart.urls', namespace='cart')),
    
    # Orders URLs 
    path('orders/', include('orders.urls', namespace='orders')),  
    path('reviews/', include('reviews.urls')),
    
    # Admin URLs
    # path('admin-panel/', admin.site.urls), 
    path('admin/', admin.site.urls),
    path('reports/', include('reports.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)