# import_products.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from products.models import Product, Category

def import_products():
    # Supprimer les anciens produits
    Product.objects.all().delete()
    print("✅ Anciens produits supprimés")
    
    # Récupérer les catégories
    categories = Category.objects.all()
    cat_dict = {cat.name: cat for cat in categories}
    
    # Liste des produits
    products = [
        {
            'name': 'iPhone 15',
            'slug': 'iphone-15',
            'price': 999.99,
            'stock': 10,
            'category': cat_dict.get('Électronique'),
            'description': 'Le dernier smartphone Apple avec puce A16 Bionic'
        },
        {
            'name': 'Samsung Galaxy S24',
            'slug': 'samsung-galaxy-s24',
            'price': 899.99,
            'stock': 15,
            'category': cat_dict.get('Électronique'),
            'description': 'Smartphone Android haut de gamme'
        },
        {
            'name': 'T-shirt Blanc',
            'slug': 'tshirt-blanc',
            'price': 19.99,
            'stock': 50,
            'category': cat_dict.get('Vêtements'),
            'description': 'T-shirt en coton bio 100%'
        },
        {
            'name': 'Jean Bleu',
            'slug': 'jean-bleu',
            'price': 49.99,
            'stock': 30,
            'category': cat_dict.get('Vêtements'),
            'description': 'Jean en denim bleu, coupe slim'
        },
        {
            'name': 'Lampe LED',
            'slug': 'lampe-led',
            'price': 29.99,
            'stock': 25,
            'category': cat_dict.get('Maison'),
            'description': 'Lampe LED design pour bureau'
        },
        {
            'name': 'Chaise Ergonomique',
            'slug': 'chaise-ergonomique',
            'price': 149.99,
            'stock': 8,
            'category': cat_dict.get('Maison'),
            'description': 'Chaise de bureau ergonomique'
        }
    ]
    
    # Créer les produits
    for product_data in products:
        product = Product.objects.create(**product_data)
        print(f"✅ {product.name} créé")
    
    print(f"\n✅ {Product.objects.count()} produits importés !")

if __name__ == '__main__':
    import_products()