# promotions/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from .models import Coupon
from cart.models import CartItem

# ============ VUES PUBLIQUES ============

@login_required
def apply_coupon(request):
    """Appliquer un code promo"""
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code', '').strip().upper()
        
        if not coupon_code:
            messages.error(request, 'Veuillez entrer un code promo.')
            return redirect('orders:checkout')
        
        try:
            coupon = Coupon.objects.get(code=coupon_code, is_active=True)
        except Coupon.DoesNotExist:
            messages.error(request, '❌ Ce code promo n\'existe pas.')
            return redirect('orders:checkout')
        
        cart_items = CartItem.objects.filter(user=request.user)
        if not cart_items:
            messages.warning(request, 'Votre panier est vide.')
            return redirect('cart:cart_view')
        
        total = sum(item.get_total() for item in cart_items)
        
        # Vérifier la validité du coupon
        is_valid, message = coupon.is_valid(total)
        
        if is_valid:
            discount = coupon.calculate_discount(total)
            total_after_discount = total - discount
            
            # Stocker en session
            request.session['coupon'] = {
                'code': coupon.code,
                'discount': float(discount),
                'total_after_discount': float(total_after_discount),
                'coupon_id': coupon.id
            }
            request.session.modified = True
            
            messages.success(request, f'✅ Code promo {coupon.code} appliqué ! Réduction de {discount:.2f}€')
        else:
            messages.error(request, f'❌ {message}')
    
    return redirect('orders:checkout')

@login_required
def remove_coupon(request):
    """Retirer le code promo appliqué"""
    if 'coupon' in request.session:
        del request.session['coupon']
        request.session.modified = True
        messages.info(request, 'Code promo retiré avec succès.')
    return redirect('orders:checkout')

# ============ VUES ADMIN ============

@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def admin_coupons(request):
    """Liste des codes promo pour l'admin"""
    coupons = Coupon.objects.all().order_by('-created_at')
    context = {
        'coupons': coupons,
        'now': timezone.now()
    }
    return render(request, 'promotions/admin_coupons.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def admin_coupon_create(request):
    """Créer un code promo"""
    if request.method == 'POST':
        code = request.POST.get('code', '').strip().upper()
        discount_type = request.POST.get('discount_type')
        discount_value = request.POST.get('discount_value')
        min_order_amount = request.POST.get('min_order_amount', 0)
        max_discount_amount = request.POST.get('max_discount_amount') or None
        valid_from = request.POST.get('valid_from')
        valid_to = request.POST.get('valid_to')
        usage_limit = request.POST.get('usage_limit', 1)
        description = request.POST.get('description', '')
        
        # Validation basique
        if not code:
            messages.error(request, 'Le code est obligatoire.')
            return render(request, 'promotions/admin_coupon_form.html')
        
        if not discount_value:
            messages.error(request, 'La valeur de réduction est obligatoire.')
            return render(request, 'promotions/admin_coupon_form.html')
        
        if not valid_from or not valid_to:
            messages.error(request, 'Les dates de validité sont obligatoires.')
            return render(request, 'promotions/admin_coupon_form.html')
        
        try:
            coupon = Coupon.objects.create(
                code=code,
                discount_type=discount_type,
                discount_value=discount_value,
                min_order_amount=min_order_amount,
                max_discount_amount=max_discount_amount,
                valid_from=valid_from,
                valid_to=valid_to,
                usage_limit=usage_limit,
                description=description,
                is_active=True
            )
            messages.success(request, f'✅ Code promo {coupon.code} créé avec succès !')
            return redirect('promotions:admin_coupons')
        except Exception as e:
            messages.error(request, f'❌ Erreur lors de la création : {str(e)}')
    
    return render(request, 'promotions/admin_coupon_form.html')

@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def admin_coupon_delete(request, coupon_id):
    """Supprimer un code promo"""
    coupon = get_object_or_404(Coupon, id=coupon_id)
    if request.method == 'POST':
        code = coupon.code
        coupon.delete()
        messages.success(request, f'✅ Code promo {code} supprimé avec succès.')
        return redirect('promotions:admin_coupons')
    return render(request, 'promotions/admin_coupon_confirm_delete.html', {'coupon': coupon})

@login_required
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def admin_coupon_toggle_status(request, coupon_id):
    """Activer/Désactiver un code promo"""
    coupon = get_object_or_404(Coupon, id=coupon_id)
    coupon.is_active = not coupon.is_active
    coupon.save()
    status = "activé" if coupon.is_active else "désactivé"
    messages.success(request, f'✅ Code promo {coupon.code} {status} avec succès.')
    return redirect('promotions:admin_coupons')