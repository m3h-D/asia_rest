from django.urls import path, include
from rest_framework.routers import DefaultRouter

from user.api.views import register_api_view, login_api_view
from product.api.views import ProductViewset
from order.api.views import OrderViewset, OrderDetailViewset
from cart.api.views import cart_view

router = DefaultRouter()
router.register('product', ProductViewset)
router.register('order', OrderViewset, basename='order')
router.register('orderitems', OrderDetailViewset, basename='orderitems')

urlpatterns = [
    path('', include(router.urls)),
    path("register/", register_api_view, name="register"),
    path("login/", login_api_view, name="login"),
    path("cart/", cart_view, name="cart_view"),
]