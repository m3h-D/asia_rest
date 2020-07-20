from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import *
from ..models import Product
from cart.api.serializers import CartSerializer, CartDeleteSerializer
import logging

logger = logging.getLogger(__name__)

class ProductViewset(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()

    @action(methods=['POST',], detail=True, url_path='add-to-cart', url_name='add-to-cart')
    def add_to_cart(self, request, pk=None):
        product = self.get_object()
        serializer = CartSerializer(data=request.data, context={"request":request, 
                                                                "product_id": product.id})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            logger.error(str(serializer.data))
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @action(methods=['DELETE',], detail=True, url_path='remove-from-cart', url_name='remove-from-cart')
    def remove_from_cart(self, request, pk=None):
        product = self.get_object()
        serializer = CartDeleteSerializer(data=request.data, context={"request":request, 
                                                                "product_id": product.id})
        if serializer.is_valid():
            serializer.delete()
            return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
        else:
            logger.error(str(serializer.data))
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)