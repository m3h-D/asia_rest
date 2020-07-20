from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from product.models import Product, Option
from cart.cart import Cart
from cart.api.serializers import CartSerializer
# Create your tests here.



class TestCart(APITestCase):

    def setUp(self):
        self.old_product = Product.objects.create(title='Product1', description="hellow", price=15000, special=False)
        self.session = self.client.session
        self.ADD_TO_CART = reverse('api:product-add-to-cart', args=(self.old_product.id,))
        self.REMOVE_FROM_CART = reverse('api:product-remove-from-cart', args=(self.old_product.id,))

    def test_add_to_cart(self):
        """test cart add results (fail and success)
        """        

        data={'amount': 5}
        
        # add to cart with simple data successfully
        cart = Cart(self.client)
        cart.add(self.old_product)
        response = self.client.post(self.ADD_TO_CART, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, data)
        self.assertEqual(len(cart), 1)

        # add new product to check length of cart
        p2 = Product.objects.create(title='Product2', description="hellow", price=15000, special=False)
        add_to = reverse('api:product-add-to-cart', args=(p2.id,))
        response2 = self.client.post(add_to, data=data)
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        cart.add(p2)
        self.assertEqual(len(cart), 2)

        add_to3 = reverse('api:product-add-to-cart', args=(5,)) # no product with this id
        response3 = self.client.post(add_to3, data=data)
        self.assertEqual(response3.status_code, status.HTTP_404_NOT_FOUND)
        seri = CartSerializer(data=data, context={"request":self.client, "product_id": 5})
        self.assertFalse(seri.is_valid())
        
        # false options data
        data2 = {
            "amount": 4,
            "option_title": "weight",
            "option_custom": 20,
        }
        response4 = self.client.post(add_to, data=data2)
        self.assertEqual(response4.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response4.json().get('non_field_errors'), ['There is no Title-Option with this title'])

        op = Option.objects.create(title='weight', product=p2)
        response5 = self.client.post(add_to, data=data2)
        self.assertEqual(response5.json().get('non_field_errors'), ['There is no Option with this id'])
        

    def test_delete_cart(self):
        """test cart delete results (fail and success)
        """        
        response = self.client.delete(self.REMOVE_FROM_CART) # product is not added to cart
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get("non_field_errors"), ['This product is not in your cart'])

        fake_url = reverse('api:product-remove-from-cart', args=(5,)) # no product with this id
        no_p = self.client.delete(fake_url)
        self.assertEqual(no_p.status_code, status.HTTP_404_NOT_FOUND)

        # add product to cart and delete it successfully
        add = self.client.post(self.ADD_TO_CART, data={'amount': 5})
        self.assertEqual(add.status_code, status.HTTP_201_CREATED)

        delete = self.client.delete(self.REMOVE_FROM_CART)
        self.assertEqual(delete.status_code, status.HTTP_204_NO_CONTENT)


