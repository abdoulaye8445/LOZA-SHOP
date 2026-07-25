# resize_images.py
import os
import django
from PIL import Image

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from products.models import Product

def resize_all_images():
    print("🔄 Redimensionnement des images...\n")
    
    for product in Product.objects.all():
        if product.image:
            img_path = product.image.path
            if os.path.exists(img_path):
                try:
                    img = Image.open(img_path)
                    original_size = img.size
                    
                    # Redimensionner à 800x800 max (conserver proportions)
                    if img.width > 800 or img.height > 800:
                        img.thumbnail((800, 800), Image.Resampling.LANCZOS)
                        img.save(img_path, quality=85, optimize=True)
                        print(f"  ✅ {product.name} : {original_size} -> {img.size}")
                    else:
                        print(f"  ℹ️ {product.name} : déjà OK ({img.size})")
                except Exception as e:
                    print(f"  ❌ Erreur pour {product.name} : {e}")
            else:
                print(f"  ❌ Fichier non trouvé : {img_path}")

if __name__ == '__main__':
    resize_all_images()