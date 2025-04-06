from django.urls import path
from .views import ChatMessageView

urlpatterns = [
    path('mensajes/', ChatMessageView.as_view(), name='chat_messages'),
]
