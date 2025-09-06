# ----- Fase 1: Construcción del Entorno -----
# Usamos una imagen oficial de Python como base.
FROM python:3.10-slim-bookworm AS builder

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Actualizamos los paquetes del sistema e instalamos herramientas de compilación
RUN apt-get update && apt-get install -y build-essential

# Creamos y activamos un entorno virtual
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copiamos el archivo de requerimientos
COPY requirements.txt .

# --- Instalación Unificada con Timeout Extendido ---
# Le damos a pip 600 segundos (10 minutos) para cada descarga.
# Esto debería ser más que suficiente para descargar los paquetes grandes de PyTorch.
RUN pip install --default-timeout=600 --no-cache-dir -r requirements.txt


# ----- Fase 2: Ejecución de la Aplicación -----
# Usamos una nueva imagen base ligera para la ejecución final
FROM python:3.10-slim-bookworm

WORKDIR /app

# Copiamos el entorno virtual con las dependencias ya instaladas
COPY --from=builder /opt/venv /opt/venv

# Copiamos el resto del código de la aplicación
COPY . .

# Activamos el entorno virtual para los comandos subsiguientes
ENV PATH="/opt/venv/bin:$PATH"

# Exponemos el puerto en el que Gunicorn se ejecutará
EXPOSE 8000

# El comando que se ejecutará cuando el contenedor inicie
# Añadimos un timeout más generoso para las llamadas a la IA
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--timeout", "120", "app:app"]

