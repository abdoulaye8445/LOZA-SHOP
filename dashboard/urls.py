# dashboard/urls.py
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('products/', views.products, name='products'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/edit/<int:pk>/', views.product_edit, name='product_edit'),
    path('products/delete/<int:pk>/', views.product_delete, name='product_delete'),
    path('orders/', views.orders, name='orders'),
    path('orders/status/<int:pk>/', views.order_status, name='order_status'),
    path('users/', views.users, name='users'),
    path('users/toggle/<int:pk>/', views.user_toggle_status, name='user_toggle_status'),
    path('categories/', views.categories, name='categories'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/edit/<int:pk>/', views.category_edit, name='category_edit'),
    path('categories/delete/<int:pk>/', views.category_delete, name='category_delete'),
]