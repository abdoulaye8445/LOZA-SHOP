# promotions/urls.py
from django.urls import path
from . import views

app_name = 'promotions'

urlpatterns = [
    path('apply/', views.apply_coupon, name='apply_coupon'),
    path('remove/', views.remove_coupon, name='remove_coupon'),
    
    # Admin URLs
    path('admin/', views.admin_coupons, name='admin_coupons'),
    path('admin/create/', views.admin_coupon_create, name='admin_coupon_create'),
    path('admin/delete/<int:coupon_id>/', views.admin_coupon_delete, name='admin_coupon_delete'),
    path('admin/toggle/<int:coupon_id>/', views.admin_coupon_toggle_status, name='admin_coupon_toggle'),
]