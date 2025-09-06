# ----- Fase 1: Construcción del Entorno -----
# Usamos una imagen oficial de Python como base.
# La versión debe coincidir con la que usaste en desarrollo (ej. 3.10)
FROM python:3.10-slim-bookworm AS builder

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Actualizamos los paquetes del sistema e instalamos build-essential
# Es necesario para compilar algunas dependencias de Python
RUN apt-get update && apt-get install -y build-essential

# Creamos un entorno virtual dentro del contenedor
# Esto es una buena práctica para mantener las dependencias aisladas
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copiamos solo el archivo de requerimientos primero para aprovechar el cache de Docker
COPY requirements.txt .

# Instalamos las dependencias dentro del entorno virtual
# La opción --no-cache-dir reduce el tamaño de la imagen
RUN pip install --no-cache-dir -r requirements.txt


# ----- Fase 2: Ejecución de la Aplicación -----
# Usamos una nueva imagen base más ligera para la ejecución final
FROM python:3.10-slim-bookworm

# Establecemos el directorio de trabajo
WORKDIR /app

# Copiamos el entorno virtual con las dependencias ya instaladas desde la fase de construcción
COPY --from=builder /opt/venv /opt/venv

# Copiamos el resto del código de la aplicación
COPY . .

# Hacemos que el entorno virtual sea el intérprete de Python por defecto
ENV PATH="/opt/venv/bin:$PATH"

# Exponemos el puerto en el que Gunicorn se ejecutará
EXPOSE 8000

# El comando que se ejecutará cuando el contenedor inicie
# Le decimos a Gunicorn que escuche en todas las interfaces de red (0.0.0.0)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]