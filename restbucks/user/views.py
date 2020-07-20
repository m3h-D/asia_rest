from django.shortcuts import render
from django.http import HttpResponse
from cart.cart import Cart
from product.models import Product

# Create your views here.
def index(request):
    cart = Cart(request)
    # cart.add(Product.objects.first())
    cart.clear()
    print(len(cart))
    return HttpResponse(len(Cart(request)))