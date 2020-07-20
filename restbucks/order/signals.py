from django.db.models.signals import pre_save, post_save, Signal
from django.dispatch import receiver
from .models import OrderItems
from cart.cart import Cart
from django.db.models import Sum


@receiver(pre_save, sender=OrderItems)
def items_total_price(sender, instance, *args, **kwargs):
    """total price for each product based on their quantity

    Args:
        sender (CLASS): the OrderItems class
        instance (OBJECT): created/updated object from orderitem
    """    
    instance.total_price = instance._get_item_price


@receiver(post_save, sender=OrderItems)
def order_total_price(sender, instance, *args, **kwargs):
    """afted calculated every items total_price(above signal) the total price of whole order 
       will be calculate here

    Args:
        sender (CLASS): the OrderItems class
        instance (OBJECT): created/updated object from orderitem
    """    
    order = instance.order
    items = sender.objects.filter(order__id=order.id)
    t_price = items.aggregate(total=Sum('total_price'))
    order.total_price = int(t_price['total'])
    order.save()
