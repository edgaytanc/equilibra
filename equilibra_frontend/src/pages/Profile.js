// src/pages/Profile.js
import React, { useState, useEffect } from 'react';
import { Container, Typography, Paper, Box, TextField, Button } from '@mui/material';
import axios from 'axios';

const Profile = () => {
  const [user, setUser] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const token = localStorage.getItem('accessToken');

  useEffect(() => {
    const fetchProfile = async () => {
      setLoading(true);
      try {
        const response = await axios.get('http://localhost:8000/api/users/profile/', {
          headers: { Authorization: `Bearer ${token}` },
        });
        setUser(response.data);
      } catch (error) {
        console.error('Error al cargar el perfil:', error);
      }
      setLoading(false);
    };

    fetchProfile();
  }, [token]);

  const handleChange = (e) => {
    setUser({ ...user, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    try {
      const response = await axios.put('http://localhost:8000/api/users/profile/', user, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setUser(response.data);
      setMessage('Perfil actualizado correctamente.');
    } catch (error) {
      console.error('Error al actualizar el perfil:', error);
      setMessage('Error al actualizar el perfil.');
    }
    setLoading(false);
  };

  return (
    <Container maxWidth="sm" sx={{ mt: 4 }}>
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Mi Perfil
        </Typography>
        {message && (
          <Typography
            variant="body2"
            color={message.startsWith('Error') ? 'error' : 'success.main'}
            sx={{ mb: 2 }}
          >
            {message}
          </Typography>
        )}
        <Box component="form" onSubmit={handleSubmit} noValidate>
          <TextField
            label="Usuario"
            name="username"
            value={user.username}
            fullWidth
            margin="normal"
            disabled
          />
          <TextField
            label="Correo electrónico"
            name="email"
            value={user.email}
            onChange={handleChange}
            fullWidth
            margin="normal"
          />
          <TextField
            label="Nombre"
            name="first_name"
            value={user.first_name}
            onChange={handleChange}
            fullWidth
            margin="normal"
          />
          <TextField
            label="Apellido"
            name="last_name"
            value={user.last_name}
            onChange={handleChange}
            fullWidth
            margin="normal"
          />
          <Button type="submit" variant="contained" color="primary" fullWidth sx={{ mt: 2 }}>
            {loading ? 'Guardando...' : 'Guardar Cambios'}
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default Profile;
