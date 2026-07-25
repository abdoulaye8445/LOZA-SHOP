# api/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db.models import Q
from django.shortcuts import get_object_or_404
from decimal import Decimal

from .serializers import *
from products.models import Product, Category, Review, Wishlist
from cart.models import CartItem
from orders.models import Order, OrderItem
from promotions.models import Coupon

# ============ AUTHENTIFICATION ============
class RegisterView(generics.CreateAPIView):
    """Inscription utilisateur"""
    permission_classes = [AllowAny]
    serializer_class = UserRegisterSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Connexion utilisateur"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        })
    return Response({'error': 'Identifiants incorrects'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Déconnexion"""
    try:
        refresh_token = request.data.get('refresh')
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Déconnecté avec succès'})
    except:
        return Response({'error': 'Token invalide'}, status=status.HTTP_400_BAD_REQUEST)

# ============ PRODUITS ============
class ProductListView(generics.ListAPIView):
    """Liste des produits avec filtres"""
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category')
        search = self.request.query_params.get('search')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        sort = self.request.query_params.get('sort')
        
        if category:
            queryset = queryset.filter(category__slug=category)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if sort == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort == 'name':
            queryset = queryset.order_by('name')
        else:
            queryset = queryset.order_by('-created_at')
        
        return queryset

class ProductDetailView(generics.RetrieveAPIView):
    """Détail d'un produit"""
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

class CategoryListView(generics.ListAPIView):
    """Liste des catégories"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

# ============ PANIER ============
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cart_view(request):
    """Voir le panier"""
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.get_total() for item in cart_items)
    serializer = CartItemSerializer(cart_items, many=True)
    return Response({
        'items': serializer.data,
        'total': total,
        'total_items': cart_items.count()
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cart_add(request):
    """Ajouter au panier"""
    product_id = request.data.get('product_id')
    quantity = request.data.get('quantity', 1)
    
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    if product.stock < quantity:
        return Response({'error': 'Stock insuffisant'}, status=status.HTTP_400_BAD_REQUEST)
    
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': quantity}
    )
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    
    return Response({'message': 'Produit ajouté au panier'})

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def cart_update(request, item_id):
    """Mettre à jour la quantité"""
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    quantity = request.data.get('quantity', 1)
    
    if quantity <= 0:
        cart_item.delete()
        return Response({'message': 'Produit supprimé du panier'})
    
    if quantity > cart_item.product.stock:
        return Response({'error': 'Stock insuffisant'}, status=status.HTTP_400_BAD_REQUEST)
    
    cart_item.quantity = quantity
    cart_item.save()
    return Response({'message': 'Panier mis à jour'})

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def cart_remove(request, item_id):
    """Supprimer du panier"""
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    return Response({'message': 'Produit supprimé du panier'})

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def cart_clear(request):
    """Vider le panier"""
    CartItem.objects.filter(user=request.user).delete()
    return Response({'message': 'Panier vidé'})

# ============ COMMANDES ============
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def orders_view(request):
    """Liste des commandes"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_detail(request, order_id):
    """Détail d'une commande"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    serializer = OrderSerializer(order)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def order_create(request):
    """Créer une commande"""
    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items:
        return Response({'error': 'Panier vide'}, status=status.HTTP_400_BAD_REQUEST)
    
    total = sum(item.get_total() for item in cart_items)
    
    # Vérifier le coupon
    coupon_code = request.data.get('coupon_code')
    coupon_discount = Decimal('0')
    coupon = None
    
    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code.upper(), is_active=True)
            is_valid, message = coupon.is_valid(total)
            if is_valid:
                coupon_discount = coupon.calculate_discount(total)
                total -= coupon_discount
                coupon.use_coupon()
        except Coupon.DoesNotExist:
            pass
    
    # Créer la commande
    order = Order.objects.create(
        user=request.user,
        total_amount=total,
        shipping_address=request.data.get('shipping_address', ''),
        payment_method=request.data.get('payment_method', 'Carte bancaire'),
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
        product = cart_item.product
        product.stock -= cart_item.quantity
        product.save()
    
    # Vider le panier
    cart_items.delete()
    
    # Envoyer email de confirmation
    try:
        from orders.views import send_order_confirmation_email
        send_order_confirmation_email(order)
    except:
        pass
    
    serializer = OrderSerializer(order)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

# ============ FAVORIS ============
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def wishlist_view(request):
    """Liste des favoris"""
    wishlist_items = Wishlist.objects.filter(user=request.user)
    serializer = WishlistSerializer(wishlist_items, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def wishlist_add(request):
    """Ajouter aux favoris"""
    product_id = request.data.get('product_id')
    product = get_object_or_404(Product, id=product_id)
    
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )
    
    if created:
        return Response({'message': 'Ajouté aux favoris'})
    return Response({'message': 'Déjà dans les favoris'})

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def wishlist_remove(request, product_id):
    """Retirer des favoris"""
    wishlist_item = get_object_or_404(Wishlist, user=request.user, product_id=product_id)
    wishlist_item.delete()
    return Response({'message': 'Retiré des favoris'})

# ============ AVIS ============
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def review_create(request, product_id):
    """Ajouter un avis"""
    product = get_object_or_404(Product, id=product_id)
    rating = request.data.get('rating')
    comment = request.data.get('comment')
    image = request.data.get('image')
    
    if not rating or not comment:
        return Response({'error': 'Note et commentaire requis'}, status=status.HTTP_400_BAD_REQUEST)
    
    review, created = Review.objects.update_or_create(
        product=product,
        user=request.user,
        defaults={
            'rating': rating,
            'comment': comment,
        }
    )
    
    if image:
        review.image = image
        review.save()
    
    return Response({'message': 'Avis ajouté'})

# ============ CODES PROMO ============
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def coupon_validate(request):
    """Vérifier un code promo"""
    code = request.data.get('code', '').upper()
    total = Decimal(str(request.data.get('total', 0)))
    
    try:
        coupon = Coupon.objects.get(code=code, is_active=True)
        is_valid, message = coupon.is_valid(total)
        if is_valid:
            discount = coupon.calculate_discount(total)
            return Response({
                'valid': True,
                'message': message,
                'discount': discount,
                'total_after_discount': total - discount
            })
        return Response({'valid': False, 'message': message}, status=status.HTTP_400_BAD_REQUEST)
    except Coupon.DoesNotExist:
        return Response({'valid': False, 'message': 'Code promo invalide'}, status=status.HTTP_400_BAD_REQUEST)