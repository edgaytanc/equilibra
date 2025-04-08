// src/pages/Login.js
import React, { useState } from 'react';
import { Container, TextField, Typography, Button, Box } from '@mui/material';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (event) => {
    event.preventDefault();
    // Aquí invocas la función de login, por ejemplo usando axios.
    console.log('Iniciando sesión...', { username, password });
  };

  return (
    <Container maxWidth="sm">
      <Typography variant="h4" gutterBottom>
        Iniciar Sesión
      </Typography>
      <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
        <TextField
          margin="normal"
          fullWidth
          id="username"
          label="Usuario"
          name="username"
          autoComplete="username"
          autoFocus
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <TextField
          margin="normal"
          fullWidth
          name="password"
          label="Contraseña"
          type="password"
          id="password"
          autoComplete="current-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <Button type="submit" fullWidth variant="contained" sx={{ mt: 3 }}>
          Iniciar Sesión
        </Button>
      </Box>
    </Container>
  );
};

export default Login;
