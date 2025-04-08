from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Conversacion, Mensaje
from .utils import analizar_mensaje

class ChatMessageView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, format=None):
        usuario = request.user
        texto_usuario = request.data.get('texto')
        conversacion_id = request.data.get('conversacion_id')
        
        # Validar que se envíe el texto del mensaje
        if not texto_usuario:
            return Response({'error': 'El campo "texto" es obligatorio.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Si se envía un ID de conversación, tratar de obtenerlo
        if conversacion_id:
            try:
                conversacion = Conversacion.objects.get(id=conversacion_id, usuario=usuario)
            except Conversacion.DoesNotExist:
                return Response({'error': 'Conversación no encontrada.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Si no se envía, se crea una nueva conversación para el usuario
            conversacion = Conversacion.objects.create(usuario=usuario)
        
        # Guardar el mensaje del usuario
        mensaje_usuario = Mensaje.objects.create(
            conversacion=conversacion,
            texto=texto_usuario,
            origen='usuario'
        )

        # Realizar el análisis del mensaje
        analisis_resultado = analizar_mensaje(texto_usuario)
        
        # Generar una respuesta dummy del ChatBot
        respuesta_dummy = "Gracias por tu mensaje. En breve te responderé."
        mensaje_chatbot = Mensaje.objects.create(
            conversacion=conversacion,
            texto=respuesta_dummy,
            origen='chatbot'
        )
        
        # Retornar la respuesta con los datos de la conversación y los mensajes
        return Response({
            'conversacion_id': conversacion.id,
            'mensaje_usuario': {
                'id': mensaje_usuario.id,
                'texto': mensaje_usuario.texto,
                'timestamp': mensaje_usuario.timestamp,
                'origen': mensaje_usuario.origen,
            },
            'mensaje_chatbot': {
                'id': mensaje_chatbot.id,
                'texto': mensaje_chatbot.texto,
                'timestamp': mensaje_chatbot.timestamp,
                'origen': mensaje_chatbot.origen,
                'analisis': analisis_resultado
            }
        }, status=status.HTTP_200_OK)


