# promotions/admin.py
from django.contrib import admin
from .models import Coupon

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_value', 'discount_type', 'min_order_amount', 
                    'valid_from', 'valid_to', 'used_count', 'usage_limit', 'is_active']
    list_filter = ['discount_type', 'is_active', 'valid_from', 'valid_to']
    search_fields = ['code', 'description']
    readonly_fields = ['used_count', 'created_at', 'updated_at']
    fieldsets = (
        ('Informations générales', {
            'fields': ('code', 'description', 'is_active')
        }),
        ('Réduction', {
            'fields': ('discount_type', 'discount_value', 'max_discount_amount', 'min_order_amount')
        }),
        ('Période de validité', {
            'fields': ('valid_from', 'valid_to')
        }),
        ('Limites d\'utilisation', {
            'fields': ('usage_limit', 'used_count')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )