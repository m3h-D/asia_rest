from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils.text import slugify
from .models import Product

@receiver(pre_save, sender=Product)
def is_offered_signal(sender, instance, *args, **kwargs):
    """check if a product has been offered

    Args:
        sender (CLASS): product class
        instance (OBJECT): an object of the product class
    """    
    if instance.offered_price and instance.offered_price > 0:
        instance.special = True

@receiver(pre_save, sender=Product)
def pre_fill_slug(sender, instance, *args, **kwargs):
    """generates slug for slug field if there is None

    Args:
        sender (CLASS): Product model as sender
        instance (OBJECT): object fo Product model
    """    
    if not instance.slug:
        try:
            instance.slug = slugify(f"{instance.title}" , allow_unicode=True)
        except:
            instance.slug = slugify(f"{instance.title}{instance.id}" , allow_unicode=True)


@receiver(post_save, sender=Product)
def update_orders(sender, instance, *args, **kwargs):
    """update orders of selected product after any changes to a product

    Args:
        sender (CLASS): Product model as sender
        instance (OBJECT): object fo Product model
    """    
    if instance.orderitems:
        for item in instance.orderitems.all():
            item.save()
