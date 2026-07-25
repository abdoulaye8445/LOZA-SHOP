# products/admin.py
from django.contrib import admin
from .models import Category, Product, Review, Wishlist

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ['name']}
    fields = ['name', 'slug', 'description', 'image']  # Ajout de image

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock', 'category', 'is_active', 'image_preview']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ['name']}
    fields = [
        'name', 'slug', 'description', 'price', 'stock', 
        'category', 'image', 'image2', 'image3', 'is_active'
    ]
    
    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="50" height="50" style="object-fit: cover;" />'
        return 'Pas d\'image'
    image_preview.allow_tags = True
    image_preview.short_description = 'Aperçu'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    fields = ['product', 'user', 'rating', 'comment', 'image']

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'added_at']