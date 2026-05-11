
# from django.contrib import admin
# from django.urls import path, include
# from django.conf import settings
# from django.conf.urls.static import static

# urlpatterns = [
#     path('admin/', admin.site.urls),           # Django default admin (we will use later)
#     path('', include('accounts.urls')),        # All our custom auth URLs
#     path('products/', include('products.urls')),
#     # path('cart/', include('cart.urls')),
#     #  path('cart/', include('cart.urls', namespace='cart')),
#      path('cart/', include('cart.urls')),
#      path('orders/', include('orders.urls', namespace='orders')),
# ]

# # Serve media files during development
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Custom URLs First (Higher Priority)
    path('', include('accounts.urls')),
    path('products/', include('products.urls')),
    path('cart/', include('cart.urls', namespace='cart')),
    path('orders/', include('orders.urls', namespace='orders')),

    # Django Admin (Keep at bottom)
    path('admin/', admin.site.urls),
    path('reports/', include('reports.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)