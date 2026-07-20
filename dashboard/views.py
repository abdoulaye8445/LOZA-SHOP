# dashboard/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from products.models import Product, Category
from orders.models import Order

def is_admin(user):
    """Vérifie si l'utilisateur est un administrateur"""
    return user.is_superuser or user.is_staff

# ============ VUES PRINCIPALES ============

@login_required
@user_passes_test(is_admin)
def index(request):
    """Page d'accueil du dashboard avec les statistiques"""
    context = {
        'total_orders': Order.objects.count(),
        'total_products': Product.objects.count(),
        'total_users': User.objects.count(),
        'total_categories': Category.objects.count(),
        'pending_orders': Order.objects.filter(status='pending').count(),
        'recent_orders': Order.objects.order_by('-created_at')[:10],
    }
    return render(request, 'dashboard/index.html', context)

# ============ GESTION DES PRODUITS ============

@login_required
@user_passes_test(is_admin)
def products(request):
    """Liste des produits"""
    products = Product.objects.all()
    return render(request, 'dashboard/products.html', {'products': products})

@login_required
@user_passes_test(is_admin)
def product_create(request):
    """Créer un nouveau produit"""
    if request.method == 'POST':
        try:
            product = Product.objects.create(
                name=request.POST.get('name'),
                slug=request.POST.get('slug'),
                description=request.POST.get('description'),
                price=request.POST.get('price'),
                stock=request.POST.get('stock'),
                category_id=request.POST.get('category'),
                is_active=request.POST.get('is_active') == 'on'
            )
            if request.FILES.get('image'):
                product.image = request.FILES.get('image')
                product.save()
            messages.success(request, 'Produit créé avec succès !')
            return redirect('dashboard:products')
        except Exception as e:
            messages.error(request, f'Erreur lors de la création : {str(e)}')
    
    categories = Category.objects.all()
    return render(request, 'dashboard/product_form.html', {'categories': categories})

@login_required
@user_passes_test(is_admin)
def product_edit(request, pk):
    """Modifier un produit existant"""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        try:
            product.name = request.POST.get('name')
            product.slug = request.POST.get('slug')
            product.description = request.POST.get('description')
            product.price = request.POST.get('price')
            product.stock = request.POST.get('stock')
            product.category_id = request.POST.get('category')
            product.is_active = request.POST.get('is_active') == 'on'
            if request.FILES.get('image'):
                product.image = request.FILES.get('image')
            product.save()
            messages.success(request, 'Produit modifié avec succès !')
            return redirect('dashboard:products')
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification : {str(e)}')
    
    categories = Category.objects.all()
    return render(request, 'dashboard/product_form.html', {
        'product': product,
        'categories': categories
    })

@login_required
@user_passes_test(is_admin)
def product_delete(request, pk):
    """Supprimer un produit"""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Produit supprimé avec succès !')
        return redirect('dashboard:products')
    return render(request, 'dashboard/product_confirm_delete.html', {'product': product})

# ============ GESTION DES COMMANDES ============

@login_required
@user_passes_test(is_admin)
def orders(request):
    """Liste des commandes"""
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'dashboard/orders.html', {'orders': orders})

@login_required
@user_passes_test(is_admin)
def order_status(request, pk):
    """Changer le statut d'une commande"""
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Statut de la commande #{order.order_number} mis à jour !')
    return redirect('dashboard:orders')

# ============ GESTION DES UTILISATEURS ============

@login_required
@user_passes_test(is_admin)
def users(request):
    """Liste des utilisateurs"""
    users = User.objects.all()
    return render(request, 'dashboard/users.html', {'users': users})

@login_required
@user_passes_test(is_admin)
def user_toggle_status(request, pk):
    """Activer/Désactiver un utilisateur"""
    user = get_object_or_404(User, pk=pk)
    if not user.is_superuser:
        user.is_active = not user.is_active
        user.save()
        status = "activé" if user.is_active else "désactivé"
        messages.success(request, f'Utilisateur {user.username} {status} avec succès !')
    return redirect('dashboard:users')

# ============ GESTION DES CATÉGORIES ============

@login_required
@user_passes_test(is_admin)
def categories(request):
    """Liste des catégories"""
    categories = Category.objects.all()
    return render(request, 'dashboard/categories.html', {'categories': categories})

@login_required
@user_passes_test(is_admin)
def category_create(request):
    """Créer une nouvelle catégorie"""
    if request.method == 'POST':
        try:
            Category.objects.create(
                name=request.POST.get('name'),
                slug=request.POST.get('slug'),
                description=request.POST.get('description')
            )
            messages.success(request, 'Catégorie créée avec succès !')
        except Exception as e:
            messages.error(request, f'Erreur lors de la création : {str(e)}')
    return redirect('dashboard:categories')

@login_required
@user_passes_test(is_admin)
def category_edit(request, pk):
    """Modifier une catégorie"""
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        try:
            category.name = request.POST.get('name')
            category.slug = request.POST.get('slug')
            category.description = request.POST.get('description')
            category.save()
            messages.success(request, 'Catégorie modifiée avec succès !')
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification : {str(e)}')
    return redirect('dashboard:categories')

@login_required
@user_passes_test(is_admin)
def category_delete(request, pk):
    """Supprimer une catégorie"""
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Catégorie supprimée avec succès !')
        return redirect('dashboard:categories')
    return render(request, 'dashboard/category_confirm_delete.html', {'category': category})