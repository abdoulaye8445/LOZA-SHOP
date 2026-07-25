# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')), 
    path('', include('products.urls')),
    path('accounts/', include('accounts.urls')),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('promotions/', include('promotions.urls')),

    # config/urls.py
    # ...
    path('newsletter/', include('newsletter.urls')),
    path('notifications/', include('notifications.urls')),
]

if settings.DEBUG:
       urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
       urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
