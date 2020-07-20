from cart.cart import Cart
from rest_framework.authtoken.models import Token
import logging

logger = logging.getLogger(__name__)

class ClearCartMiddleware:
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)
        

    def process_view(self, request, view_func, view_args, view_kwargs):
        header_token = request.META.get('HTTP_AUTHORIZATION')
        if header_token is not None or request.user.is_authenticated:
            try:
                token = header_token.split(" ")[-1]
                token_obj = Token.objects.get(key=token)
                request.user = token_obj.user
            except Token.DoesNotExist as e:
                logger.warning(str(e))
            
            else:
                cart = Cart(request)
                if len(cart) > 0:
                    for order in request.user.order.all():
                        if order.status in ("preparation", "ready", "delivered"):
                            product_ids = [item.product.id for item in order.orderitems.all()]
                            cart.remove(product_ids)