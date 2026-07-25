# blog/urls.py
from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.blog_home, name='blog_home'),
    path('search/', views.blog_search, name='blog_search'),
    path('<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('category/<slug:slug>/', views.blog_category, name='blog_category'),
]