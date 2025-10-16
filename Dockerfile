# ----- Fase 1: Construcción del Entorno -----
FROM python:3.10-slim-bookworm AS builder

WORKDIR /app
RUN apt-get update && apt-get install -y build-essential

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt .
RUN pip install --default-timeout=600 --no-cache-dir -r requirements.txt


# ----- Fase 2: Ejecución de la Aplicación -----
FROM python:3.10-slim-bookworm

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY . .

ENV PATH="/opt/venv/bin:$PATH"

# ***** NUEVAS LÍNEAS *****
# Hacemos que nuestro script de entrada sea ejecutable
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

# ***** LÍNEA MODIFICADA *****
# El CMD ahora se gestionará en docker-compose.yml para mayor flexibilidad,
# pero dejamos un ENTRYPOINT aquí como buena práctica.
ENTRYPOINT ["/app/entrypoint.sh"]