from decimal import Decimal
from rest_framework import serializers
from .models import Cart, CartItem, Product, Collection, Review

class ProductSerializer(serializers.ModelSerializer):
    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')
    collection = serializers.HyperlinkedRelatedField(
        queryset = Collection.objects.all(),
        view_name='collection-detail'
    )

    def calculate_tax(self, product: Product):
        return product.price * Decimal(1.1)
    
    class Meta:
        model = Product
        fields = ['id', 'title', 'slug', 'description', 'price', 'inventory', 'price_with_tax', 'collection']


class CollectionSerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']

class ReviewSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        product_id = self.context['product_id']
        return Review.objects.create(product_id=product_id, **validated_data)
    
    class Meta:
        model = Review
        fields = ['id', 'date', 'name', 'description']
        
    
class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'price']

class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cartItem: CartItem):
        return cartItem.quantity * cartItem.product.price
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']
    
class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    
    def get_total_price(self, cart):
        return sum([item.quantity * item.product.price for item in cart.items.all()])
    
    class Meta:
        model = Cart
        fields = ['id', 'total_price', 'items']
    
class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('No product with the given id was found.')
        return value

    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']

        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)
        return self.instance

    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']

class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']