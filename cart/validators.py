# cart/validators.py (créer ce fichier)
from django.core.exceptions import ValidationError

def validate_quantity(value):
    if value < 1:
        raise ValidationError('La quantité doit être supérieure à 0.')
    if value > 999:
        raise ValidationError('La quantité ne peut pas dépasser 999.')