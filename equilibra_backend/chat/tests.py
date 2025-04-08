from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

class ChatEndpointTests(APITestCase):
    def setUp(self):
        # Crear un usuario y obtener un token de acceso
        self.user = User.objects.create_user(username="chatuser", email="chatuser@example.com", password="testpassword123")
        self.client = APIClient()
        login_url = reverse('token_obtain_pair')
        response = self.client.post(login_url, {'username': 'chatuser', 'password': 'testpassword123'}, format='json')
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    def test_send_message(self):
        url = reverse('chat_messages')  # Asegúrate de que en chat/urls.py el endpoint tenga el nombre 'chat_messages'
        data = {
            "texto": "Hola, estoy muy estresado hoy."
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Se espera que la respuesta contenga datos de la conversación y ambos mensajes
        self.assertIn('conversacion_id', response.data)
        self.assertIn('mensaje_usuario', response.data)
        self.assertIn('mensaje_chatbot', response.data)
        # También se puede verificar que el análisis se encuentre en el mensaje del chatbot
        self.assertIn('analisis', response.data['mensaje_chatbot'])
