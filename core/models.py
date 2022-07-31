import uuid

from django.contrib.auth.models import User
from django.db import models


# Create your models here.


class Product(models.Model):
    name = models.CharField(max_length=512)
    price = models.DecimalField(max_digits=1000, decimal_places=2)
    minimum = models.IntegerField()
    amount_per_package = models.IntegerField(verbose_name='amount-per-package')
    max_availability = models.BigIntegerField(verbose_name='max-availability')

    def __str__(self):
        return f'{self.name}'


class ShoppingCart(models.Model):
    user = models.OneToOneField(User, related_name='user_cart', blank=True, on_delete=models.PROTECT, unique=True)

    def __str__(self):
        return f'{self.user}'


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, related_name='user_order', blank=True, on_delete=models.PROTECT)


class ShoppingProduct(models.Model):
    shopping_cart = models.ForeignKey(ShoppingCart, related_name='shopping_cart', blank=True, null=True,
                                      on_delete=models.PROTECT)
    product = models.ForeignKey(Product, related_name='products', on_delete=models.PROTECT)
    quantity = models.BigIntegerField(verbose_name='quantity')
    order = models.ForeignKey(Order, related_name='order_products', blank=True, null=True, on_delete=models.PROTECT)

    @property
    def partial_price(self):
        return self.product.price * self.quantity

    @property
    def package_integrity(self):
        if self.quantity % self.product.amount_per_package == 0:
            return True
        else:
            return False

    def __str__(self):
        return f'{self.product} | {self.quantity}'

    class Meta:
        unique_together = [['shopping_cart', 'product']]
