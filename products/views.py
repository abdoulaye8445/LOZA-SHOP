# products/views.py
from django.shortcuts import render, get_object_or_404
from .models import Product, Category

def home(request):
    """Page d'accueil avec tous les produits actifs"""
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'products/home.html', context)

def product_detail(request, slug):
    """Page de détail d'un produit"""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, 'products/product_detail.html', {'product': product})

def product_list(request):
    """Liste de tous les produits"""
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()
    return render(request, 'products/product_list.html', {
        'products': products,
        'categories': categories
    })