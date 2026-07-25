# promotions/models.py
from django.db import models
from django.utils import timezone
from decimal import Decimal

class Coupon(models.Model):
    DISCOUNT_TYPES = [
        ('percentage', 'Pourcentage (%)'),
        ('fixed', 'Montant fixe (€)'),
    ]
    
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES, default='percentage')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    usage_limit = models.IntegerField(default=1, help_text="Nombre maximum d'utilisations")
    used_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Code promo'
        verbose_name_plural = 'Codes promo'
    
    def is_valid(self, order_total=0):
        """Vérifie si le coupon est valide"""
        now = timezone.now()
        
        if not self.is_active:
            return False, "Ce code promo n'est pas actif."
        
        if self.used_count >= self.usage_limit:
            return False, "Ce code promo a atteint sa limite d'utilisation."
        
        if self.valid_from > now:
            return False, f"Ce code promo n'est pas encore valide (disponible à partir du {self.valid_from.strftime('%d/%m/%Y')})."
        
        if self.valid_to < now:
            return False, "Ce code promo a expiré."
        
        if order_total < self.min_order_amount:
            return False, f"Le montant minimum pour ce code promo est de {self.min_order_amount}€."
        
        return True, "Code promo valide !"
    
    def calculate_discount(self, order_total):
        """Calcule la réduction"""
        if self.discount_type == 'percentage':
            discount = order_total * (self.discount_value / 100)
            if self.max_discount_amount:
                discount = min(discount, self.max_discount_amount)
        else:  # fixed
            discount = self.discount_value
        
        return min(discount, order_total)
    
    def use_coupon(self):
        """Incrémente le compteur d'utilisation"""
        self.used_count += 1
        self.save()
    
    def __str__(self):
        return f"{self.code} - {self.discount_value}{'%' if self.discount_type == 'percentage' else '€'}"