// src/App.js
import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Login from './pages/Login';
import Chat from './pages/Chat';
import Profile from './pages/Profile';

function App() {
  return (
    <BrowserRouter>
      {/* Puedes agregar un componente de navegación común aquí, como un Navbar */}
      <Routes>
        {/* Define las rutas */}
        <Route path="/login" element={<Login />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/profile" element={<Profile />} />
        {/* Ruta por defecto (puedes redirigir a /login o /chat) */}
        <Route path="*" element={<Login />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
