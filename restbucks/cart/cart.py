from django.conf import settings
from product.models import Product
from product.api.serializers import ProductSerializer

# Create your models here.

class Cart:
    """session cart that will store users product in session instead of model
    """    
    def __init__(self, request):
        """get the session 'cart' if exists else create an empty one

        Args:
            request (HTTP REQUEST): to define session
        """
        self.request = request
        self.session = request.session
        cart = self.session.get(settings.CART_ID)
        if not cart:
            cart = self.session[settings.CART_ID] = {}
        self.cart = cart

    def add(self, product, customization=None, amount=None):
        """add product to session but only the id, price and customizations

        Args:
            product (OBJECT): a product object that selected by user
            customization (LIST, optional): a list of dictionaries that contains the selected options. Defaults to None.
            amount (int, optional): the quantity of product that user wants to buy. Defaults to 1.
        """        
        product_id = str(product.id)
        product_price = str(product.offered_price) if product.offered_price else str(product.price)
        amount = -1 if amount == 0 else amount # to seprate False from zero
        if product_id not in self.cart:
            self.cart[product_id] = {
                'amount': amount if amount else 1,
                'price': product_price,
                'customization': customization
            }
        else:
            if amount:
                if amount == -1:
                    self.remove(product_id)
                else:
                    self.cart[product_id]['amount'] = amount
            else:
                self.cart[product_id]['amount'] += 1
            if self.cart:
                self.cart[product_id]['customization'] = customization
        self.save()
    
    def save(self):
        """just to make sure the cart has been updated
        """        
        self.session[settings.CART_ID] = self.cart
        self.session.modified = True
    
    def remove(self, product_ids):
        """remove list of selected products from cart session

        Args:
            product_ids (LIST): list of selected products
        """  
        for product_id in product_ids:      
            if str(product_id) in self.cart:
                del self.cart[str(product_id)]
                self.save()
    
    def clear(self):
        """empty the sessoin cart
        """        
        self.session[settings.CART_ID] = {}
        self.session.modified = True

    def __iter__(self):
        product_ids = self.cart.keys()
        products = ProductSerializer(Product.objects.filter(id__in=product_ids), context={'request': self.request}, many=True)
        for product in products.data:
            self.cart[str(product.get("id"))]['product'] = product # to render product attributes
        
        for item in self.cart.values():
            item['price'] = int(item['price'])
            item['total_price'] = item['price'] * item['amount']

            yield item


    def __len__(self):
        return sum(item['amount'] for item in self.cart.values())
    
    def get_total_price(self):
        return sum(int(item['price']) * item['amount'] for item in self.cart.values())