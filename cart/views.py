# cart/views.py - Vérifiez que cette fonction existe
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from products.models import Product
from .models import CartItem

@login_required
def cart_view(request):
    """Afficher le panier"""
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.get_total() for item in cart_items)
    return render(request, 'cart/cart.html', {
        'cart_items': cart_items,
        'total': total
    })

@login_required
def add_to_cart(request, product_id):
    """Ajouter un produit au panier"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    if product.stock <= 0:
        messages.error(request, f'Désolé, {product.name} est en rupture de stock.')
        return redirect('products:product_detail', slug=product.slug)
    
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f'Un autre {product.name} ajouté au panier !')
        else:
            messages.warning(request, f'Stock insuffisant pour {product.name}')
    else:
        messages.success(request, f'{product.name} ajouté au panier !')
    
    return redirect('cart:cart_view')

@login_required
def remove_from_cart(request, product_id):
    """Retirer un produit du panier (diminuer quantité)"""
    product = get_object_or_404(Product, id=product_id)
    cart_item = get_object_or_404(CartItem, user=request.user, product=product)
    
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
        messages.info(request, f'Quantité de {product.name} réduite.')
    else:
        cart_item.delete()
        messages.info(request, f'{product.name} retiré du panier.')
    
    return redirect('cart:cart_view')

@login_required
def delete_from_cart(request, product_id):
    """Supprimer complètement un produit du panier"""
    product = get_object_or_404(Product, id=product_id)
    cart_item = get_object_or_404(CartItem, user=request.user, product=product)
    cart_item.delete()
    messages.info(request, f'{product.name} supprimé du panier.')
    return redirect('cart:cart_view')

@login_required
def clear_cart(request):
    """Vider complètement le panier"""
    CartItem.objects.filter(user=request.user).delete()
    messages.info(request, 'Votre panier a été vidé.')
    return redirect('cart:cart_view')