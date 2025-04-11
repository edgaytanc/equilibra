// src/pages/Chat.js
import React, { useState } from 'react';
import { Container, Typography, Paper, List, Box, TextField, Button } from '@mui/material';
import axios from 'axios';
import Message from '../components/Message';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  // Función para enviar el mensaje
  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    // Agrega el mensaje del usuario a la lista local
    const userMessage = { origen: 'usuario', texto: input, timestamp: new Date().toISOString() };
    setMessages((prev) => [...prev, userMessage]);

    try {
      // Envia el mensaje al backend (reemplaza la URL si es necesario)
      const response = await axios.post(
        'http://localhost:8000/api/chat/mensajes/',
        { texto: input },
        { headers: { Authorization: `Bearer ${localStorage.getItem('accessToken')}` } }
      );
      // Se espera que la respuesta incluya el mensaje del ChatBot
      const chatbotMessage = response.data.mensaje_chatbot;
      setMessages((prev) => [...prev, chatbotMessage]);
    } catch (error) {
      console.error('Error al enviar el mensaje:', error);
    }
    setInput('');
  };

  return (
    <Container maxWidth="md">
      <Typography variant="h4" align="center" gutterBottom sx={{ mt: 4 }}>
        ChatBot Psicológico
      </Typography>
      <Paper sx={{ height: '60vh', overflowY: 'auto', p: 2, mb: 2, backgroundColor: '#f9f9f9' }}>
        <List>
          {messages.map((msg, index) => (
            <Message key={index} message={msg} />
          ))}
        </List>
      </Paper>
      <Box component="form" onSubmit={handleSend} sx={{ display: 'flex', gap: 2, mb: 4 }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Escribe tu mensaje..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <Button type="submit" variant="contained" color="primary">
          Enviar
        </Button>
      </Box>
    </Container>
  );
};

export default Chat;
