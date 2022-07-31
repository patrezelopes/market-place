from django.urls import include
from django.urls.conf import path
from rest_framework.routers import DefaultRouter

from core import views

router = DefaultRouter()
router.register(r'products', views.ProductViewSet, basename='products')
router.register(r'shopping_cart', views.ShoppingCartViewSet, basename='shopping-cart')
checkout = views.ShoppingCartViewSet.as_view({'post': 'checkout'})

urlpatterns = [
    path('', include(router.urls)),
    path('checkout/', checkout, name='checkout'),
]
