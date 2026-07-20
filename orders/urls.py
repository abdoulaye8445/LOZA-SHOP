# orders/urls.py
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('', views.order_list, name='orders'),  # Changé de orders à order_list
    path('download-receipt/<int:order_id>/', views.download_receipt, name='download_receipt'),
]