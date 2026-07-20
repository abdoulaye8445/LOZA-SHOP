# cart/context_processors.py
from .models import CartItem

def cart_total(request):
    if request.user.is_authenticated:
        total_items = CartItem.objects.filter(user=request.user).count()
    else:
        cart = request.session.get('cart', {})
        total_items = sum(cart.values())
    return {'cart_total_items': total_items}