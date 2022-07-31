
from django.contrib import admin
# Register your models here.

from .models import Product, ShoppingProduct, ShoppingCart

admin.site.register(Product)
admin.site.register(ShoppingProduct)
admin.site.register(ShoppingCart)
