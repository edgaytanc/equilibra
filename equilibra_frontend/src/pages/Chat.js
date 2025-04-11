// src/pages/Chat.js
import React, { useState } from 'react';
import {
  Container,
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import axios from 'axios';

const Chat = () => {
  const [inputText, setInputText] = useState('');
  const [messages, setMessages] = useState([]);

  // Manejar el envío del mensaje
  const handleSend = async (event) => {
    event.preventDefault();
    if (!inputText.trim()) return;

    // Guarda el mensaje del usuario en la lista local
    const userMessage = {
      origen: 'usuario',
      texto: inputText,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);

    try {
      // Realiza la petición POST al endpoint del chat
      const response = await axios.post(
        'http://localhost:8000/api/chat/mensajes/',
        {
          texto: inputText,
          // Opción: agregar conversacion_id si ya la tienes.
        },
        {
          headers: {
            // Se asume que ya tienes almacenado el token en localStorage
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );

      // Extrae la respuesta del ChatBot del endpoint
      const chatbotMessage = response.data.mensaje_chatbot;
      setMessages((prev) => [...prev, chatbotMessage]);
    } catch (error) {
      console.error('Error al enviar el mensaje:', error);
      // Aquí puedes agregar una notificación de error si lo deseas.
    }
    setInputText('');
  };

  return (
    <Container maxWidth="md">
      <Typography variant="h4" align="center" gutterBottom sx={{ mt: 4 }}>
        ChatBot Psicológico
      </Typography>

      {/* Área de mensajes */}
      <Paper
        sx={{
          height: '60vh',
          overflowY: 'auto',
          p: 2,
          mb: 2,
          backgroundColor: '#f9f9f9',
        }}
      >
        <List>
          {messages.map((msg, index) => (
            <ListItem key={index} sx={{ 
              justifyContent: msg.origen === 'usuario' ? 'flex-end' : 'flex-start'
            }}>
              <ListItemText
                primary={msg.origen === 'usuario' ? 'Tú' : 'ChatBot'}
                secondary={msg.texto}
                sx={{
                  textAlign: msg.origen === 'usuario' ? 'right' : 'left',
                }}
              />
            </ListItem>
          ))}
        </List>
      </Paper>

      {/* Formulario para enviar mensajes */}
      <Box
        component="form"
        onSubmit={handleSend}
        sx={{ display: 'flex', gap: 2, mb: 4 }}
      >
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Escribe tu mensaje..."
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
        />
        <Button type="submit" variant="contained" color="primary">
          Enviar
        </Button>
      </Box>
    </Container>
  );
};

export default Chat;
