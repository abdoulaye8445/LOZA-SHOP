# blog/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import BlogPost, BlogCategory, BlogComment
from .forms import BlogCommentForm

def blog_home(request):
    posts = BlogPost.objects.filter(is_published=True).order_by('-created_at')
    categories = BlogCategory.objects.all()
    
    paginator = Paginator(posts, 6)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    
    context = {
        'posts': posts,
        'categories': categories,
    }
    return render(request, 'blog/blog_home.html', context)

def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    post.views += 1
    post.save()
    
    recent_posts = BlogPost.objects.filter(is_published=True).exclude(id=post.id)[:5]
    categories = BlogCategory.objects.all()
    
    if request.method == 'POST':
        form = BlogCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            messages.success(request, 'Votre commentaire a été ajouté !')
            return redirect('blog:blog_detail', slug=post.slug)
    else:
        form = BlogCommentForm()
    
    context = {
        'post': post,
        'recent_posts': recent_posts,
        'categories': categories,
        'form': form,
    }
    return render(request, 'blog/blog_detail.html', context)

def blog_category(request, slug):
    category = get_object_or_404(BlogCategory, slug=slug)
    posts = BlogPost.objects.filter(category=category, is_published=True)
    categories = BlogCategory.objects.all()
    
    paginator = Paginator(posts, 6)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    
    context = {
        'category': category,
        'posts': posts,
        'categories': categories,
    }
    return render(request, 'blog/blog_category.html', context)

def blog_search(request):
    query = request.GET.get('q', '')
    posts = BlogPost.objects.filter(
        Q(title__icontains=query) | Q(content__icontains=query),
        is_published=True
    )
    categories = BlogCategory.objects.all()
    
    context = {
        'posts': posts,
        'categories': categories,
        'query': query,
    }
    return render(request, 'blog/blog_search.html', context)