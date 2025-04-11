// src/pages/Profile.js
import React, { useState, useEffect } from 'react';
import { Container, Typography, Box, TextField, Button, Paper } from '@mui/material';
import axios from 'axios';

const Profile = () => {
  // Estado para almacenar la información del perfil
  const [profile, setProfile] = useState({
    id: '',
    username: '',
    email: '',
    first_name: '',
    last_name: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Función para obtener los datos del perfil del usuario al cargar el componente
  useEffect(() => {
    const fetchProfile = async () => {
      setLoading(true);
      try {
        const token = localStorage.getItem('token'); // Se asume que el token se almacena en localStorage
        const response = await axios.get('http://localhost:8000/api/users/profile/', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setProfile(response.data);
      } catch (err) {
        setError('Error al cargar la información del perfil.');
      }
      setLoading(false);
    };

    fetchProfile();
  }, []);

  // Función para actualizar los valores del formulario
  const handleChange = (e) => {
    setProfile({ ...profile, [e.target.name]: e.target.value });
  };

  // Función para guardar los cambios en el perfil
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');
    try {
      const token = localStorage.getItem('token');
      const response = await axios.put('http://localhost:8000/api/users/profile/', profile, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setProfile(response.data);
      setSuccess('Perfil actualizado correctamente.');
    } catch (err) {
      setError('Error al actualizar el perfil.');
    }
    setLoading(false);
  };

  return (
    <Container maxWidth="sm" sx={{ mt: 4 }}>
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Mi Perfil
        </Typography>
        {error && (
          <Typography variant="body2" color="error" sx={{ mb: 2 }}>
            {error}
          </Typography>
        )}
        {success && (
          <Typography variant="body2" color="success.main" sx={{ mb: 2 }}>
            {success}
          </Typography>
        )}
        <Box component="form" onSubmit={handleSubmit} noValidate>
          <TextField
            label="Usuario"
            name="username"
            value={profile.username}
            fullWidth
            margin="normal"
            disabled
          />
          <TextField
            label="Correo electrónico"
            name="email"
            value={profile.email}
            onChange={handleChange}
            fullWidth
            margin="normal"
          />
          <TextField
            label="Nombre"
            name="first_name"
            value={profile.first_name}
            onChange={handleChange}
            fullWidth
            margin="normal"
          />
          <TextField
            label="Apellido"
            name="last_name"
            value={profile.last_name}
            onChange={handleChange}
            fullWidth
            margin="normal"
          />
          <Button
            type="submit"
            variant="contained"
            color="primary"
            fullWidth
            sx={{ mt: 2 }}
            disabled={loading}
          >
            {loading ? 'Guardando...' : 'Guardar Cambios'}
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default Profile;
