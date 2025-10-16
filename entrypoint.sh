#!/bin/sh

# Salir inmediatamente si un comando falla
set -e

# 1. Aplicar las migraciones de la base de datos
echo "Aplicando migraciones de la base de datos..."
flask db upgrade

# 2. Crear el usuario administrador (sembrar la base de datos)
echo "Verificando/creando usuario administrador..."
python seed.py

# 3. Iniciar la aplicación principal con Gunicorn
echo "Iniciando Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 --timeout 120 app:app