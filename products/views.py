# products/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Avg
from .models import Product, Category, Review
from .forms import ReviewForm
from .models import Wishlist


def home(request):
    products = Product.objects.filter(is_active=True)[:8]
    categories = Category.objects.all()
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'products/home.html', context)



from blog.models import BlogPost

def home(request):
    products = Product.objects.filter(is_active=True)[:8]
    categories = Category.objects.all()
    recent_posts = BlogPost.objects.filter(is_published=True).order_by('-created_at')[:3]
    
    context = {
        'products': products,
        'categories': categories,
        'recent_posts': recent_posts,
    }
    return render(request, 'products/home.html', context)

# products/views.py - Ajouter ces fonctions

@login_required
def toggle_wishlist_ajax(request):
    """Ajouter/Retirer des favoris via AJAX"""
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        
        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            product=product
        )
        
        if not created:
            wishlist_item.delete()
            return JsonResponse({'status': 'removed', 'message': 'Retiré des favoris'})
        
        return JsonResponse({'status': 'added', 'message': 'Ajouté aux favoris'})
    
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    
    similar_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]
    
    reviews = product.reviews.all()
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    if request.user.is_authenticated:
        existing_review = Review.objects.filter(product=product, user=request.user).first()
        form = ReviewForm(instance=existing_review)
    else:
        form = None
    
    context = {
        'product': product,
        'similar_products': similar_products,
        'reviews': reviews,
        'average_rating': round(average_rating, 1),
        'reviews_count': reviews.count(),
        'form': form,
    }
    return render(request, 'products/product_detail.html', context)

def product_list(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()
    
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    sort = request.GET.get('sort')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'name':
        products = products.order_by('name')
    else:
        products = products.order_by('-created_at')
    
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    context = {
        'products': products,
        'categories': categories,
        'current_category': category_slug,
        'min_price': min_price,
        'max_price': max_price,
        'sort': sort,
    }
    return render(request, 'products/product_list.html', context)

def search_products(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(is_active=True)
    
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )
    
    context = {
        'products': products,
        'query': query,
        'count': products.count()
    }
    return render(request, 'products/search_results.html', context)

@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review, created = Review.objects.update_or_create(
                product=product,
                user=request.user,
                defaults={
                    'rating': form.cleaned_data['rating'],
                    'comment': form.cleaned_data['comment'],
                }
            )
            if created:
                messages.success(request, 'Votre avis a été ajouté avec succès !')
            else:
                messages.success(request, 'Votre avis a été mis à jour !')
        else:
            messages.error(request, 'Veuillez corriger les erreurs.')
    
    return redirect('products:product_detail', slug=product.slug)


@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )
    if created:
        messages.success(request, f'{product.name} ajouté à votre liste de souhaits !')
    else:
        wishlist_item.delete()
        messages.info(request, f'{product.name} retiré de votre liste de souhaits.')
    return redirect('products:product_detail', slug=product.slug)

@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'products/wishlist.html', {'wishlist_items': wishlist_items})