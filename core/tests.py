import itertools
import json
from collections import OrderedDict
from decimal import Decimal
from urllib.parse import urlencode

import pytest
from django.contrib.auth import get_user_model

# Create your tests here.
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from core.exceptions import ProductQuantityExceeded, ProductPackageIntegrity, ProductDoesNotExist
from core.models import ShoppingProduct, ShoppingCart, Product
from core.utils import valid_quantity
from core.views import ShoppingCartViewSet, ProductViewSet
from rest_framework.test import APIClient
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

pytestmark = pytest.mark.django_db

User = get_user_model()


@pytest.fixture
def user_data():
    return {
        "username": "test_user",
        "password": "test password",
        "email": "valid@email.com",
    }


@pytest.fixture
def created_user(user_data):
    password = user_data.pop("password")
    user = User(**user_data)
    user.set_password(password)
    user.save()
    return user


@pytest.fixture
def user_data2():
    return {
        "username": "test_user2",
        "password": "test password",
        "email": "valid2@email.com",
    }


@pytest.fixture
def created_user2(user_data2):
    password = user_data2.pop("password")
    user = User(**user_data2)
    user.set_password(password)
    user.save()
    return user


@pytest.fixture
def shopping_cart(created_user):
    return ShoppingCart.objects.create(user=created_user)


@pytest.fixture
def shopping_cart2(created_user2):
    return ShoppingCart.objects.create(user=created_user2)


@pytest.fixture
def product():
    return Product.objects.create(name="any name", price=Decimal("1000.00"),
                                  minimum=12, amount_per_package=12,
                                  max_availability=5000)


@pytest.fixture
def product2():
    return Product.objects.create(name="any other name", price=Decimal("100.00"),
                                  minimum=2, amount_per_package=2,
                                  max_availability=5000)


@pytest.fixture
def product_inserted(shopping_cart, product):
    return ShoppingProduct.objects.create(shopping_cart=shopping_cart,
                                          product=product,
                                          quantity=24)


@pytest.fixture
def product_inserted2(shopping_cart2, product):
    return ShoppingProduct.objects.create(shopping_cart=shopping_cart2,
                                          product=product,
                                          quantity=24)


@pytest.fixture
def product_inserted3(shopping_cart, product2):
    return ShoppingProduct.objects.create(shopping_cart=shopping_cart,
                                          product=product2,
                                          quantity=24)


@pytest.fixture
def product_inserted_quantity_exceed(shopping_cart, product):
    return ShoppingProduct(shopping_cart=shopping_cart,
                           product=product,
                           quantity=10000)


@pytest.fixture
def product_inserted_package_split(shopping_cart, product):
    return ShoppingProduct(shopping_cart=shopping_cart,
                           product=product,
                           quantity=13)


def test_valid_quantity(product_inserted):
    assert valid_quantity(product_inserted) is True


def test_invalid_quantity_exceed(product_inserted_quantity_exceed):
    with pytest.raises(ProductQuantityExceeded) as excinfo:
        valid_quantity(product_inserted_quantity_exceed)
    assert str(excinfo.value) == 'Product quantity exceed'


def test_invalid_quantity_package_split(product_inserted_package_split):
    with pytest.raises(ProductPackageIntegrity) as excinfo:
        valid_quantity(product_inserted_package_split)
    assert str(excinfo.value) == 'Product package could not be split'


def test_product_partial_price(product_inserted):
    assert product_inserted.partial_price == Decimal("1000.00") * 24


@pytest.fixture
def token(rf, created_user):
    url = reverse('token_obtain_pair')
    request_ok = rf.post(url)
    request_ok.data = {
        "username": created_user.username,
        "password": "test password"
    }
    s = TokenObtainPairSerializer(data=request_ok.data)
    s.is_valid()
    client = APIClient()
    return s.validated_data['access']


@pytest.fixture
def shopping_cart_post_ok(rf, token):
    url = reverse('shopping-cart-list')
    request_ok = rf.post(url)
    request_ok.headers = {'Authorization': f'Bearer {token}'}
    request_ok.content_type = 'application/json'
    request_ok.user = created_user
    request_ok.data = {
        "product": 1,
        "quantity": 12
    }
    return request_ok


def test_insert_product(created_user, product):
    url = reverse('shopping-cart-list')
    factory = APIRequestFactory()
    user = created_user
    view = ShoppingCartViewSet.as_view({'post': 'create'})
    request = factory.post(url, data={
        "product": product.pk,
        "quantity": 12
    })
    force_authenticate(request, user=user)
    response = view(request)
    assert response.status_code == status.HTTP_201_CREATED


def test_increase_product_quantity(created_user, product):
    url = reverse('shopping-cart-list')
    factory = APIRequestFactory()
    user = created_user
    view = ShoppingCartViewSet.as_view({'post': 'create'})
    request = factory.post(url, data={
        "product": product.pk,
        "quantity": 12
    })
    force_authenticate(request, user=user)
    for _ in itertools.repeat(None, 4):
        view(request)
    product_inserted = ShoppingProduct.objects.get(shopping_cart__user=created_user, product=product)
    assert product_inserted.quantity == 48


def test_product_package_integrity_error(created_user, product):
    url = reverse('shopping-cart-list')
    factory = APIRequestFactory()
    user = created_user
    view = ShoppingCartViewSet.as_view({'post': 'create'})
    request = factory.post(url, data={
        "product": product.pk,
        "quantity": product.amount_per_package + 1
    })
    force_authenticate(request, user=user)
    response = view(request).render()
    assert json.loads(response.content) == {'detail': 'Product package could not be split'}


def test_product_quantity_exceed(created_user, product):
    url = reverse('shopping-cart-list')
    factory = APIRequestFactory()
    user = created_user
    view = ShoppingCartViewSet.as_view({'post': 'create'})
    request = factory.post(url, data={
        "product": product.pk,
        "quantity": product.max_availability + 1
    })
    force_authenticate(request, user=user)
    response = view(request).render()
    assert json.loads(response.content) == {'detail': 'Product quantity exceed'}


def test_insert_product_does_not_exist(shopping_cart_post_ok, created_user):
    url = reverse('shopping-cart-list')
    factory = APIRequestFactory()
    user = created_user
    view = ShoppingCartViewSet.as_view({'post': 'create'})
    request = factory.post(url, data={
        "product": 999,
        "quantity": 12
    })
    force_authenticate(request, user=user)
    response = view(request).render()
    assert json.loads(response.content) == {'detail': 'Product requested does not exist'}


def test_update_product(created_user, product_inserted):
    url = reverse('shopping-cart-detail', kwargs={'pk': product_inserted.pk})
    factory = APIRequestFactory()
    user = created_user
    view = ShoppingCartViewSet.as_view({'patch': 'partial_update'})

    request = factory.patch(url, data={
        "quantity": 12

    })
    force_authenticate(request, user=user)
    response = view(request, pk=product_inserted.pk)
    assert response.status_code == status.HTTP_200_OK


def test_update_product_wrong_user(created_user, product_inserted2):
    url = reverse('shopping-cart-detail', kwargs={'pk': product_inserted2.pk})
    factory = APIRequestFactory()
    user = created_user
    view = ShoppingCartViewSet.as_view({'patch': 'partial_update'})

    request = factory.patch(url, data={
        "quantity": 12

    })
    force_authenticate(request, user=user)
    response = view(request, pk=product_inserted2.pk).render()
    assert json.loads(response.content) == {'detail': 'Product request fail'}


def test_update_product_not_found(created_user):
    url = reverse('shopping-cart-detail', kwargs={'pk': 999})
    factory = APIRequestFactory()
    user = created_user
    view = ShoppingCartViewSet.as_view({'patch': 'partial_update'})

    request = factory.patch(url, data={
        "quantity": 12

    })
    force_authenticate(request, user=user)
    response = view(request, pk=999).render()
    assert json.loads(response.content) == {'detail': 'Not found.'}


def test_update_product_wrong_field(created_user, product_inserted):
    url = reverse('shopping-cart-detail', kwargs={'pk': product_inserted.pk})
    factory = APIRequestFactory()
    user = created_user
    view = ShoppingCartViewSet.as_view({'patch': 'partial_update'})

    request = factory.patch(url, data={
        "wrong": 12

    })
    force_authenticate(request, user=user)
    response = view(request, pk=product_inserted.pk).render()
    assert json.loads(response.content) == {'detail': 'Product wrong field'}


def test_checkout(created_user, product_inserted):
    url = reverse('checkout')
    factory = APIRequestFactory()
    user = created_user
    view = ShoppingCartViewSet.as_view({'post': 'checkout'})

    request = factory.post(url)
    force_authenticate(request, user=user)
    response = view(request)
    assert response.status_code == status.HTTP_200_OK


def test_checkout_fail_max_availability_exceed(created_user, product_inserted):
    product_inserted.quantity = product_inserted.product.minimum - 1
    product_inserted.save()
    url = reverse('checkout')
    factory = APIRequestFactory()
    user = created_user
    view = ShoppingCartViewSet.as_view({'post': 'checkout'})

    request = factory.post(url)
    force_authenticate(request, user=user)
    response = view(request).render()
    assert json.loads(response.content) == {'detail': f'any name - minimum: {product_inserted.product.minimum} - '
                                                      f'Requested: {product_inserted.quantity}'}


def test_get_shopping_cart(created_user, product_inserted, product_inserted3):
    url = reverse('products-list')
    factory = APIRequestFactory()
    user = created_user
    view = ShoppingCartViewSet.as_view({'get': 'list'})

    request = factory.get(url)
    force_authenticate(request, user=user)
    response = view(request)
    assert response.status_code == status.HTTP_200_OK


def test_get_product_list(created_user, product_inserted, product_inserted3):
    url = reverse('products-list')
    factory = APIRequestFactory()
    user = created_user
    view = ProductViewSet.as_view({'get': 'list'})
    request = factory.get(url)
    force_authenticate(request, user=user)
    response = view(request)
    assert response.status_code == status.HTTP_200_OK


def test_get_product_list_filtered(created_user, product_inserted, product_inserted3):
    query_params = {'name': 'other'}
    url = reverse('products-list')
    factory = APIRequestFactory()
    user = created_user
    view = ProductViewSet.as_view({'get': 'list'})
    request = factory.get(url, query_params)
    force_authenticate(request, user=user)
    response = view(request)
    assert response.data.get('results')[0]['name'] == "any other name"
