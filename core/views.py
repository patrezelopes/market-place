from django.shortcuts import render

# Create your views here.
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.models import Product, ShoppingProduct
from core.serializers import ProductSerializer, ShoppingProductSerializer, OrderSerializer


class ProductViewSet(viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = [IsAuthenticated, ]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (filters.SearchFilter,)

    def filter_queryset(self, queryset):
        return queryset.filter(name__icontains=self.request.query_params.get('name', ''))


class ShoppingCartViewSet(viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = [IsAuthenticated, ]
    queryset = ShoppingProduct.objects.filter(shopping_cart__isnull=False)
    serializer_class = ShoppingProductSerializer

    def get_products(self, request):
        shopping_cart_products = ShoppingProduct.objects.filter(shopping_cart__user=request.user)
        total_price = sum(map(lambda products: products.partial_price, shopping_cart_products))
        return total_price, shopping_cart_products

    def list(self, request, *args, **kwargs):
        response = super().list(request, args, kwargs)
        total_price, shopping_cart_products = self.get_products(request)
        response.data = dict(total_price=total_price, **response.data)
        return response

    def checkout(self, request, *args, **kwargs):
        response = super().list(request, args, kwargs)
        total_price, shopping_cart_products = self.get_products(request)
        order_serializer = OrderSerializer()
        order_serializer.create(request)
        response.data = dict(total_price=total_price, **response.data)
        return response
