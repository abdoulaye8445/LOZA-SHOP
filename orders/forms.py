# orders/forms.py
from django import forms
from .models import Order

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['shipping_address', 'payment_method']
        widgets = {
            'shipping_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Votre adresse de livraison'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-select'
            }, choices=[
                ('Carte bancaire', 'Carte bancaire'),
                ('PayPal', 'PayPal'),
                ('Virement bancaire', 'Virement bancaire'),
            ]),
        }
        labels = {
            'shipping_address': 'Adresse de livraison',
            'payment_method': 'Moyen de paiement',
        }