from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from cart.models import CartItem
from .models import Order, OrderItem
from .forms import CheckoutForm
import json
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

@login_required
def checkout(request):
    """Page de validation de commande"""
    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items:
        messages.warning(request, 'Votre panier est vide !')
        return redirect('products:home')
    
    total = sum(item.get_total() for item in cart_items)
    
    # Vérifier le stock
    for item in cart_items:
        if item.product.stock < item.quantity:
            messages.error(request, f'Stock insuffisant pour {item.product.name}')
            return redirect('cart:cart_view')
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Créer la commande
            order = Order.objects.create(
                user=request.user,
                total_amount=total,
                shipping_address=form.cleaned_data['shipping_address'],
                payment_method=form.cleaned_data['payment_method'],
                is_paid=True,
                status='confirmed'
            )
            
            # Créer les items
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
            
            messages.success(request, f'Votre commande {order.order_number} a été validée avec succès !')
            
            return render(request, 'orders/order_confirmation.html', {
                'order': order,
                'order_items': order.items.all()
            })
    else:
        form = CheckoutForm()
    
    return render(request, 'orders/checkout.html', {
        'form': form,
        'cart_items': cart_items,
        'total': total
    })

@login_required
def order_list(request):
    """Liste des commandes de l'utilisateur"""
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': user_orders})

@login_required
def orders(request):
    """Alias pour order_list (pour compatibilité)"""
    return order_list(request)

@login_required
def download_receipt(request, order_id):
    """Télécharger le reçu en PDF"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="recu_{order.order_number}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Titre
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.blue,
        spaceAfter=30
    )
    elements.append(Paragraph(f'Reçu de commande', title_style))
    elements.append(Spacer(1, 12))
    
    # Informations
    info_style = ParagraphStyle('InfoStyle', parent=styles['Normal'], fontSize=12)
    elements.append(Paragraph(f'<b>Numéro de commande :</b> {order.order_number}', info_style))
    elements.append(Paragraph(f'<b>Date :</b> {order.created_at.strftime("%d/%m/%Y %H:%M")}', info_style))
    elements.append(Paragraph(f'<b>Client :</b> {order.user.username}', info_style))
    elements.append(Spacer(1, 12))
    
    # Tableau
    data = [['Produit', 'Quantité', 'Prix unitaire', 'Total']]
    for item in order.items.all():
        data.append([
            item.product.name,
            str(item.quantity),
            f'{item.price:.2f} €',
            f'{item.get_total():.2f} €'
        ])
    
    data.append(['', '', 'Total', f'{order.total_amount:.2f} €'])
    
    table = Table(data, colWidths=[2.5*inch, 1*inch, 1.5*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.beige),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -2), 1, colors.black),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 24))
    elements.append(Paragraph('Merci pour votre confiance !', styles['Normal']))
    
    doc.build(elements)
    return response