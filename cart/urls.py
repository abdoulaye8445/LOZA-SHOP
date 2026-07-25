# cart/urls.py
from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_view, name='cart_view'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('delete/<int:product_id>/', views.delete_from_cart, name='delete_from_cart'),
    path('clear/', views.clear_cart, name='clear_cart'),
]