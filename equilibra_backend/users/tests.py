from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status

class AuthenticationTests(APITestCase):
    def test_user_registration(self):
        url = reverse('register')  # Asegúrate de que el nombre de la URL sea 'register'
        data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword123"
        }
        response = self.client.post(url, data, format='json')
        # Para la vista de registro, normalmente se devuelve un 201 Created.
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], "testuser")

    def test_user_login(self):
        # Creamos el usuario primero
        user = User.objects.create_user(username="testuser", email="testuser@example.com", password="testpassword123")
        url = reverse('token_obtain_pair')  # Asegúrate de que el nombre en urls sea 'token_obtain_pair'
        data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Se deben devolver los tokens 'access' y 'refresh'
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
