from django.db import models
from django.contrib.auth.models import User

class Conversacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversaciones')
    fecha_inicio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation de {self.usuario.username} iniciada el {self.fecha_inicio}"

class Mensaje(models.Model):
    ORIGEN_CHOICES = [
        ('usuario', 'Usuario'),
        ('chatbot', 'Chatbot'),
    ]
    conversacion = models.ForeignKey(Conversacion, on_delete=models.CASCADE, related_name='mensajes')
    texto = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    origen = models.CharField(max_length=10, choices=ORIGEN_CHOICES)

    
    def __str__(self):
        return f"Mensaje de {self.origen} en {self.conversacion} a las {self.timestamp}"
