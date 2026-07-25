# products/recommendations.py
from .models import Product, OrderItem

def get_recommendations(user, limit=4):
    """Recommandations basées sur les achats précédents"""
    if not user.is_authenticated:
        return Product.objects.filter(is_active=True).order_by('-created_at')[:limit]
    
    # Produits déjà achetés
    purchased_products = OrderItem.objects.filter(
        order__user=user
    ).values_list('product_id', flat=True)
    
    # Catégories des produits achetés
    purchased_categories = Product.objects.filter(
        id__in=purchased_products
    ).values_list('category_id', flat=True)
    
    # Recommandations par catégorie
    recommendations = Product.objects.filter(
        category__id__in=purchased_categories,
        is_active=True
    ).exclude(id__in=purchased_products).distinct()[:limit]
    
    # Si pas assez de recommandations, compléter avec les produits les plus vendus
    if recommendations.count() < limit:
        top_selling = Product.objects.filter(is_active=True).order_by('-stock')[:limit]
        recommendations = list(recommendations) + list(top_selling)
        recommendations = recommendations[:limit]
    
    return recommendations