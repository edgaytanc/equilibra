// src/components/ProtectedRoute.js
import React, { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ children }) => {
  const { auth } = useContext(AuthContext);
  // Si no hay token de acceso, redirige a la página de login
  if (!auth || !auth.accessToken) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

export default ProtectedRoute;
