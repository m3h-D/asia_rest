from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, viewsets
from ..cart import Cart
from .serializers import *
from rest_framework.renderers import JSONRenderer
import logging

logger = logging.getLogger(__name__)

@api_view(["GET", "PUT", "PATCH"])
def cart_view(request):
    """get the cart and get specific data of cart for retrieve and update

    Args:
        request (HTTP REQUEST): to call Cart and send data

    Returns:
        JSON: response as serialized data
    """    
    cart = Cart(request)
    cart_data = [{"total_price": cart.get_total_price()},]
    for c in cart:
        cart_data.append({
            "product_id": c.get("product")['id'] ,
            "amount": c.get("amount") ,
            "product_price": c.get("total_price") ,
            "product_title": c.get('product')['title'],
            "customization": c.get("customization"),
        })
    if request.method == "GET":
        serializer = CartDetailSerializer(cart_data, many=True)
        return Response(serializer.data)
    elif request.method == "PUT" or request.method == "PATCH":
        serializer = CartDetailSerializer(cart_data, many=True, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        else:
            logger.error(str(serializer.errors))
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST) 
