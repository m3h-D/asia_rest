from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.serializers import AuthTokenSerializer
from .api.serializers import RegisterSerializer

User = get_user_model()

REGISTER_URL = reverse('api:register')
LOGIN_URL = reverse('api:login')

class TestRegister(APITestCase):

    def setUp(self):
        self.old_user = User.objects.create(email='mahdi@email.com')

    def test_validate_email(self):
        data = {
            'email': 'mahdi@email.com',
            'password': 'supersecretpassword'
        }
        new_data = {
            'email': 'rst@email.com',
            'password': 'supersecretpassword123'
        }
        exist_user = User.objects.filter(email=data.get('email'))
        self.assertTrue(exist_user.exists())
        response = self.client.post(REGISTER_URL, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())

        response = self.client.post(REGISTER_URL, data={'password': 'supersecret324'})
        self.assertEqual(response.json().get('email'), ["This field is required."])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(REGISTER_URL, data=new_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get("username"), new_data.get('email').split("@")[0])

    def test_validate_password(self):
        short_data = {
            'email': 'abc@email.com',
            'password': '123'
        }
        con_data = {
            'email': 'abc@email.com',
            'password': 'helloworld'
        }
        response = self.client.post(REGISTER_URL, data=short_data)
        serializer = RegisterSerializer(data=short_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(response.json().get('password'), ["Pssword length should be atleast 8 characters"])

        response = self.client.post(REGISTER_URL, data=con_data)
        serializer = RegisterSerializer(data=con_data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(response.json().get('password'), ["password should contains numbers and letters"])


class TestLogin(APITestCase):
    def setUp(self):
        self.exists_data = {
            'username': 'asdf@gmail.com',
            'password': 'secret123456',
        }
        self.user = User.objects.create(email=self.exists_data.get('username'))
        self.user.set_password(self.exists_data.get("password"))
        self.user.save()
    
    def test_login(self):
        data = {
            'username': 'sadfsdaf@yahoo.com',
            'password': 'secret1345'
        }
        response = self.client.post(LOGIN_URL, data)
        self.assertFalse(AuthTokenSerializer(data=data).is_valid())
        
        response = self.client.post(LOGIN_URL, self.exists_data)
        self.assertTrue(AuthTokenSerializer(data=self.exists_data).is_valid())
        self.assertEqual(response.data.get('token'), self.user.auth_token.key)