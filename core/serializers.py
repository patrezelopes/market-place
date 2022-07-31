from django.db import IntegrityError, transaction
from django.db.transaction import TransactionManagementError
from rest_framework import serializers

from core.exceptions import ProductError, ProductQuantity, ProductPackageIntegrity, ProductDoesNotExist, \
    ProductWrongField
from core.models import Product, ShoppingCart, ShoppingProduct, Order
from core.utils import valid_quantity


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = '__all__'


class ShoppingProductSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    price = serializers.CharField(source='product.price', read_only=True)
    minimum = serializers.CharField(source='product.minimun', read_only=True)
    amount_per_package = serializers.CharField(source='product.amount_per_package', read_only=True)

    class Meta:
        model = ShoppingProduct
        fields = ['id', 'product_name', 'price', 'minimum', 'amount_per_package', 'quantity']

    @transaction.atomic(savepoint=False)
    def create(self, request):
        shopping_car, created = ShoppingCart.objects.get_or_create(user=self.context['request'].user)
        try:
            product = Product.objects.get(pk=self.initial_data.get('product'))
        except (IntegrityError, Product.DoesNotExist):
            raise ProductDoesNotExist
        quantity = int(self.initial_data.get('quantity'))
        try:
            product_inserted = ShoppingProduct.objects.get(shopping_cart=shopping_car,
                                                           product=product)
            product_inserted.quantity += quantity
        except ShoppingProduct.DoesNotExist:
            product_inserted = ShoppingProduct(shopping_cart=shopping_car,
                                               product=product,
                                               quantity=quantity)
        if valid_quantity(product_inserted):
            product_inserted.save()
        return product_inserted

    def update(self, instance, validated_data):
        try:
            quantity = validated_data.get('quantity')
            product_inserted = instance
            if product_inserted.shopping_cart.user == self.context['request'].user:
                product_inserted.quantity = quantity
                if valid_quantity(product_inserted):
                    product_inserted.save()
                    return product_inserted
            else:
                raise ProductError
        except TypeError:
            raise ProductWrongField


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

    @transaction.atomic(savepoint=True)
    def create(self, request):
        user = request.user
        order = Order.objects.create(user=user)
        shopping_products = ShoppingProduct.objects.filter(shopping_cart__user=user)
        for shopping_product in shopping_products:
            if shopping_product.quantity >= shopping_product.product.minimum:
                shopping_product.shopping_cart = None
                shopping_product.order = order
                shopping_product.save()
            else:
                raise ProductQuantity(
                    detail=f'{shopping_product.product.name} - minimum: {shopping_product.product.minimum} - Requested: {shopping_product.quantity}')
        return order
