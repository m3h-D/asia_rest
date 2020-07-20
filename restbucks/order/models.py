from django.db import models, transaction
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import JSONField
from product.models import Product, CHOICES
from .tasks import send_email
from cart.cart import Cart
import logging

# Create your models here.

logger = logging.getLogger(__name__)
User = get_user_model()

LOCATION = (
    ('take_away', _('take away')),
    ('in_shop', _('in shop')),
)


STATUS = (
    ('waiting', _("You have ordered your product.")),
    ('preparation', _("Your order is preparing")),
    ('ready', _("Your Order is ready")),
    ('delivered', _("Your Order has been delivered")),
)



class OrderItems(models.Model):
    order = models.ForeignKey('Order', models.CASCADE, 'orderitems', verbose_name=_('Order'))
    product = models.ForeignKey(Product, models.PROTECT, 'orderitems', verbose_name=_("Product"))
    amount = models.SmallIntegerField(_("Amount"), default=1)
    customizations = JSONField(blank=True, null=True)
    total_price = models.PositiveIntegerField(default=0, verbose_name=_("Total price"), blank=True, null=True)

    @property
    def _get_item_price(self):
        try:
            price = self.product.offered_price if self.product.offered_price else self.product.price
            item_price = int(self.amount) * int(price)
            return int(item_price)
        except Exception as e:
            logger.warning(str(e))




class OrderManager(models.Manager):
    def get_or_create_order(self, request, location):
        cart = Cart(request)
        try:
            with transaction.atomic():
                order, created = self.get_or_create(user=request.user, 
                                                    status='waiting',
                                                    consume_location=str(location))

                for item in Cart(request):
                    customizations = {}
                    product = get_object_or_404(Product, id=item['product']['id'])
                    for k, v in item['customization'].items():
                        title = product.option.get(title=k)
                        c_o = title.customazition.get(id=int(v))
                        customizations.update({str(title.title): str(c_o.c_option)})
                    OrderItems.objects.get_or_create(order=order,
                                            product=product,
                                            amount=item['amount'],
                                            customizations=customizations
                                            )
                return order
        except Exception as e:
            logger.warning(str(e))
            return str(e)





class Order(models.Model):
    user = models.ForeignKey(User, models.PROTECT, 'order', verbose_name=_("User"))
    status = models.CharField(_("Status"), max_length=11, choices=STATUS, default='waiting')
    consume_location = models.CharField(_("Consume Location"), max_length=9, choices=LOCATION)
    total_price = models.PositiveIntegerField(verbose_name=_("Totla Price"), default=0, blank=True, null=True)
    canceled = models.BooleanField(_("Canceled Order"), default=False)
    created_date = models.DateTimeField(_("Created Date"), auto_now_add=True)
    updated_date = models.DateTimeField(_("Updated Date"), auto_now=True)
    objects = OrderManager()

    __changed_status = None

    def __init__(self, *args, **kwargs):
        """save the current(previous) status to a privaite variable
           to check if the status has been changed
        """        
        super().__init__(*args, **kwargs)
        self.__changed_status = self.status


    def save(self, *args, **kwargs):
        """calculate total price of the order and send an email if
           status of order has been changed.
        """     
        if self.__changed_status != self.status:
            send_email.delay(self.user.email, self.get_status_display())
        super().save(*args, **kwargs)
        self.__changed_status = self.status
