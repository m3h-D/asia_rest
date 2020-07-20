from rest_framework import viewsets, status
from ..models import Order, OrderItems
from rest_framework.response import Response
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
import logging

logger = logging.getLogger(__name__)

class OrderDetailViewset(viewsets.ModelViewSet):
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # if self.request.user.is_staff:
        #     return OrderItems.objects.all()
        return OrderItems.objects.filter(order__in=self.request.user.order.all())

    def get_serializer_class(self):
        if self.action in 'retrieve':
            return  OrderItemDetailSerializer
        return self.serializer_class
    



class OrderViewset(viewsets.ModelViewSet):
    """shows all requested user orders

    Args:
        viewsets ([type]): [description]

    Returns:
        JSON: returns serialized data
    """    
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # if self.request.user.is_staff:
        #     return Order.objects.all()
        return self.request.user.order.filter(canceled=False)

    def get_serializer_class(self):
        """if action is retieve, update or destory user DetailSerializer
           else it will user default serializer class

        Returns:
            OBJECT: returns serializer class
        """        
        if self.action in ("retrieve", "destroy"):
            return OrderDetailSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """custom create action

        Args:
            serializer (OBJECT): default serializer class
        """
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors)
        

    def update(self, request, *args, **kwargs):
        """custom update action

        Args:
            serializer (OBJECT): DetailSerialzer
        """        
        instance = self.get_object()
        serializer = OrderDetailSerializer(instance, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            logger.error(str(serializer.data))
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)