# orders/views.py

import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from decimal import Decimal  # <-- AJOUTER CET IMPORT
from cart.models import CartItem
from .models import Order, OrderItem
from .forms import CheckoutForm
from promotions.models import Coupon
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime


stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def create_payment_intent(request):
    """Créer une intention de paiement Stripe"""
    try:
        cart_items = CartItem.objects.filter(user=request.user)
        if not cart_items:
            return JsonResponse({'error': 'Panier vide'}, status=400)
        
        total = sum(item.get_total() for item in cart_items)
        
        # Appliquer coupon si présent
        coupon_data = request.session.get('coupon')
        if coupon_data:
            total = Decimal(str(coupon_data.get('total_after_discount', total)))
        
        # Convertir en centimes pour Stripe
        amount = int(total * 100)
        
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='eur',
            metadata={
                'user_id': request.user.id,
                'user_email': request.user.email
            }
        )
        return JsonResponse({
            'clientSecret': intent.client_secret,
            'amount': amount
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def stripe_webhook(request):
    """Webhook Stripe pour confirmer les paiements"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        # Traiter le paiement réussi
        # Créer la commande ici
        pass
    
    return HttpResponse(status=200)


# ============ FONCTION D'ENVOI D'EMAIL ============
def send_order_confirmation_email(order):
    """Envoyer un email de confirmation de commande"""
    subject = f'Confirmation de votre commande #{order.order_number}'
    html_message = render_to_string('orders/email_confirmation.html', {'order': order})
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [order.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        print(f"✅ Email envoyé à {order.user.email}")
    except Exception as e:
        print(f"❌ Erreur d'envoi d'email : {e}")

# ============ VUE CHECKOUT ============
@login_required
def checkout(request):
    """Page de validation de commande avec gestion des coupons"""
    cart_items = CartItem.objects.filter(user=request.user)
    
    # Vérifier si le panier est vide
    if not cart_items:
        messages.warning(request, 'Votre panier est vide !')
        return redirect('products:home')
    
    # Calculer le total
    total = sum(item.get_total() for item in cart_items)
    
    # Vérifier le stock
    for item in cart_items:
        if item.product.stock < item.quantity:
            messages.error(request, f'Stock insuffisant pour {item.product.name}')
            return redirect('cart:cart_view')
    
    # Gérer le coupon en session
    coupon_data = request.session.get('coupon')
    total_after_discount = total
    discount_amount = Decimal('0.00')  # <-- CHANGER EN Decimal
    coupon_code = None
    
    if coupon_data:
        discount_amount = Decimal(str(coupon_data.get('discount', 0)))  # <-- CONVERTIR EN Decimal
        total_after_discount = total - discount_amount
        coupon_code = coupon_data.get('code')
    
    # Traitement du formulaire POST
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Utiliser le total après réduction si un coupon est appliqué
            final_total = total_after_discount if coupon_data else total
            
            # Créer la commande
            order = Order.objects.create(
                user=request.user,
                total_amount=final_total,
                shipping_address=form.cleaned_data['shipping_address'],
                payment_method=form.cleaned_data['payment_method'],
                is_paid=True,
                status='confirmed'
            )
            
            # Créer les items de la commande
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
                # Réduire le stock
                product = cart_item.product
                product.stock -= cart_item.quantity
                product.save()
            
            # Vider le panier
            cart_items.delete()
            
            # Gérer le coupon utilisé
            if coupon_data:
                coupon_id = coupon_data.get('coupon_id')
                if coupon_id:
                    try:
                        coupon = Coupon.objects.get(id=coupon_id)
                        coupon.use_coupon()
                        print(f"✅ Coupon {coupon.code} utilisé ({coupon.used_count}/{coupon.usage_limit})")
                    except Coupon.DoesNotExist:
                        pass
                
                # Supprimer le coupon de la session
                del request.session['coupon']
                request.session.modified = True
            
            # Envoyer l'email de confirmation
            send_order_confirmation_email(order)
            
            messages.success(request, f'✅ Votre commande {order.order_number} a été validée avec succès !')
            
            return render(request, 'orders/order_confirmation.html', {
                'order': order,
                'order_items': order.items.all()
            })
    else:
        form = CheckoutForm()
    
    # Contexte pour le template
    context = {
        'form': form,
        'cart_items': cart_items,
        'total': total,
        'total_after_discount': total_after_discount,
        'discount_amount': discount_amount,
        'coupon_code': coupon_code,
        'has_coupon': bool(coupon_data)
    }
    
    return render(request, 'orders/checkout.html', context)

# ============ VUE LISTE DES COMMANDES ============
@login_required
def order_list(request):
    """Liste des commandes de l'utilisateur"""
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': user_orders})

@login_required
def orders(request):
    """Alias pour order_list (pour compatibilité)"""
    return order_list(request)

# ============ VUE TÉLÉCHARGEMENT REÇU ============
@login_required
def download_receipt(request, order_id):
    """Télécharger le reçu en PDF"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="recu_{order.order_number}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2E4057'),
        spaceAfter=30,
        alignment=1
    )
    
    info_style = ParagraphStyle(
        'InfoStyle',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=6,
    )
    
    elements.append(Paragraph('📄 REÇU DE COMMANDE', title_style))
    elements.append(Spacer(1, 20))
    
    elements.append(Paragraph(f'<b>Numéro de commande :</b> {order.order_number}', info_style))
    elements.append(Paragraph(f'<b>Date :</b> {order.created_at.strftime("%d/%m/%Y à %H:%M")}', info_style))
    elements.append(Paragraph(f'<b>Client :</b> {order.user.get_full_name() or order.user.username}', info_style))
    elements.append(Paragraph(f'<b>Email :</b> {order.user.email}', info_style))
    elements.append(Paragraph(f'<b>Statut :</b> {order.get_status_display()}', info_style))
    elements.append(Spacer(1, 10))
    
    elements.append(Paragraph('<b>Adresse de livraison</b>', info_style))
    elements.append(Paragraph(order.shipping_address.replace('\n', '<br/>'), info_style))
    elements.append(Spacer(1, 20))
    
    data = [['Produit', 'Quantité', 'Prix unitaire', 'Total']]
    
    for item in order.items.all():
        data.append([
            item.product.name,
            str(item.quantity),
            f'{item.price:.2f} €',
            f'{item.get_total():.2f} €'
        ])
    
    data.append(['', '', 'Total TTC', f'{order.total_amount:.2f} €'])
    
    table = Table(data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
    
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E4057')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -2), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -2), 8),
        ('TOPPADDING', (0, 1), (-1, -2), 8),
        ('BACKGROUND', (2, -1), (-1, -1), colors.HexColor('#2E4057')),
        ('TEXTCOLOR', (2, -1), (-1, -1), colors.whitesmoke),
        ('FONTNAME', (2, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (2, -1), (-1, -1), 14),
        ('BOTTOMPADDING', (2, -1), (-1, -1), 12),
        ('TOPPADDING', (2, -1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -2), 1, colors.HexColor('#CCCCCC')),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#2E4057')),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 30))
    
    thank_style = ParagraphStyle(
        'ThankStyle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor('#2E4057'),
        alignment=1,
        fontName='Helvetica-Bold'
    )
    elements.append(Paragraph('Merci pour votre confiance !', thank_style))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph('Nous espérons vous revoir bientôt dans notre boutique.', 
                             ParagraphStyle('NormalCenter', parent=styles['Normal'], alignment=1)))
    elements.append(Spacer(1, 20))
    
    footer_style = ParagraphStyle(
        'FooterStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#999999'),
        alignment=1
    )
    elements.append(Paragraph('---', footer_style))
    elements.append(Paragraph(f'Ce reçu a été généré le {datetime.now().strftime("%d/%m/%Y à %H:%M")}', footer_style))
    elements.append(Paragraph('© 2026 LOZA Shop - Tous droits réservés', footer_style))
    
    doc.build(elements)
    return response