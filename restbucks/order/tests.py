from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from rest_framework import status
from django.urls import reverse
from .models import Order, OrderItems
from cart.cart import Cart
from product.models import Product, Customazition, Option
from .api.serializers import OrderSerializer, OrderDetailSerializer

User = get_user_model()

ORDER_CREATE_URL = reverse('api:order-list')

class TestOrder(APITestCase):

    def setUp(self):
        data = {'amount': 2,
                "option_title": None,
                "option_custom": None,}
        self.client = APIClient ()
        self.user = User.objects.create_user(username='saam', password="supersecretpass123")
        self.client.force_authenticate(self.user)
        self.cart = Cart(self.client)
        c_option = Customazition.objects.bulk_create([
                                                    Customazition(c_option='semi'),
                                                    Customazition(c_option='single'),
                                                    Customazition(c_option='whole'),
                                                    Customazition(c_option='ginger'),])
        self.product1 =  Product.objects.create(title='Product1', description="hellow", price=15000, special=False)
        options = Option.objects.bulk_create([
                                            Option(title='shots', product=self.product1),
                                            Option(title='kind', product=self.product1),])
        options[0].customazition.add(c_option[0], c_option[1])
        options[1].customazition.add(c_option[2], c_option[3])
        data['option_title'] = [self.product1.option.first().title, self.product1.option.last().title ]
        data['option_custom'] =  [self.product1.option.first().customazition.first().id,
                                self.product1.option.last().customazition.first().id]
        rs = self.client.post(reverse('api:product-add-to-cart', args=(self.product1.id,)), data=data)
        self.assertEqual(rs.status_code, status.HTTP_201_CREATED)

    def test_create_orders(self):
        """to test create an order from cart
        """
        # create order with invalid consume_location (fail)
        data = {'consume_location': 'blah blah'}
        serializer = OrderSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        response = self.client.post(ORDER_CREATE_URL, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get("consume_location"), [f'"{data["consume_location"]}" is not a valid choice.'])


        # create order with valid consume_location (success)
        response2 = self.client.post(ORDER_CREATE_URL, data={'consume_location': 'in_shop'})
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        serializer = OrderSerializer(data={'consume_location': 'in_shop'})
        self.assertTrue(serializer.is_valid())

        # check the order is created
        order_url = reverse('api:order-detail', args=(response2.data['id'],))
        response3 = self.client.get(order_url)
        self.assertEqual(response3.status_code, status.HTTP_200_OK)


    def test_update_orders(self):
        """to test the view function to update created order
        """        
        response = self.client.post(ORDER_CREATE_URL, data={'consume_location': 'take_away'}) # create an order
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        update_url = reverse("api:order-detail", args=(response.data['id'],)) 

        # patch only Order table data (success)
        data = {'consume_location': 'in_shop'}
        response2 = self.client.patch(update_url, data=data)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.data['consume_location'], data['consume_location'])

        # patch only Order table data (fail)
        data = {'consume_location': 'o lala'}
        response3 = self.client.patch(update_url, data=data)
        self.assertEqual(response3.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response3.json().get("consume_location"), [f'"{data["consume_location"]}" is not a valid choice.'])

        # update orderitems amount and customization (success)
        data1 = {
            "orderitems": [
                {
                    "amount": 3,
                    "product": 2,
                    "customizations": {
                        "kind": "whole"
                    }
                }
            ]
        }

        response4 = self.client.patch(update_url, data=data1, format='json')
        self.assertEqual(response4.status_code, status.HTTP_200_OK)
        self.assertEqual(response4.data['orderitems'][0]['amount'], data1['orderitems'][0]['amount'])
        self.assertEqual(response4.data['orderitems'][0]['customizations'], data1['orderitems'][0]['customizations'])

        # update customization value (invalid key)
        data1 = {
            "orderitems": [
                {
                    "amount": 3,
                    "product": 2,
                    "customizations": {
                        "size": "choclate_chip"
                    }
                }
            ]
        }
        
        response5 = self.client.patch(update_url, data=data1, format='json')
        self.assertEqual(response5.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response5.json().get("Option_title"), ["Invalid option title"])

        # update customization value (invalid value)
        data1 = {
            "orderitems": [
                {
                    "amount": 3,
                    "product": 2,
                    "customizations": {
                        "kind": "choclate_chip"
                    }
                }
            ]
        }
        
        response6 = self.client.patch(update_url, data=data1, format='json')
        self.assertEqual(response6.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response6.json().get("Option_customazition"), ["Invalid customazition value"])