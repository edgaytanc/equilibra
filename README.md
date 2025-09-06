# Elena: Prototipo de Chatbot de Apoyo Emocional

Elena es una aplicación web en desarrollo que funciona como un asistente conversacional de apoyo emocional. Su objetivo principal es actuar como un sistema de triaje inteligente, detectando posibles señales de malestar psicológico (ansiedad, estrés) en los usuarios y remitiendo los casos que requieren atención a profesionales de la salud mental registrados en la plataforma.

Este proyecto está construido con Python, Flask, SQLAlchemy, y utiliza modelos de IA de Google (Gemini) para la conversación y de Hugging Face para la detección de sentimientos.

## ✅ Características Actuales (Fase 2 Completada)

* **Registro y Autenticación de Usuarios:** Sistema completo de registro e inicio de sesión con contraseñas seguras (hasheadas).
* **Roles de Usuario:** Diferenciación entre roles de `paciente` y `psicólogo`.
* **Chat Persistente:** Las conversaciones con el chatbot Kai se guardan en una base de datos y se pueden revisar.
* **Detección de Malestar:** La IA analiza las conversaciones en tiempo real para detectar patrones de sentimiento negativo.
* **Sistema de Remisión Automática:** Los pacientes que muestran un malestar persistente son marcados automáticamente como "requiere revisión".
* **Dashboard para Psicólogos:** Un portal seguro donde los psicólogos pueden iniciar sesión para ver una lista de los pacientes marcados.
* **Visualización de Casos:** Los psicólogos pueden revisar el historial completo de la conversación de un paciente para evaluar la situación.

---

## 🚀 Guía de Instalación y Puesta en Marcha

Sigue estos pasos para poner en marcha el proyecto en un entorno de desarrollo local.

### 1. Requisitos Previos

* Python 3.10 o superior.
* Git (para clonar el repositorio).

### 2. Instalación

**a. Clonar el Repositorio**
```bash
    git clone <URL_DE_TU_REPOSITORIO>
    cd chatbot_prototipo

**b. Crear y Activar el Entorno Virtual**

En Linux/macOS:
```bash
    python3 -m venv env
    source env/bin/activate


En Windows (cmd):
```cmd
    python -m venv env
    .\env\Scripts\activate```

**c. instalar dependencias**

```
pip install -r requirements.txt```

### 2. Puesta en marcha
El demo ya incluye una base de datos done ya puede interactuar.
Incluye un usuario psicologo con las credenciales usuario: dr_rivera y password: clavesegura123
puede crear un usuario paciente desde el login

Si no funciona debe crear una nueva base de datos, estos son los pasos:


**a.  Crear y migrar la base de datos**
Si es la primera vez que ejecutas el proyecto, necesitas inicializar la base de datos.

* Configura la variable de entorno de Flask:
    Linux/macOS: export FLASK_APP=app.py
    Windows: set FLASK_APP=app.py

* Ejecuta los comandos de migración:
    ```flask db init
    flask db migrate -m "Initial migration"
    flask db upgrade```

**b. Poner en marcha el servidor de forma local**
Finalmente, inicia el servidor de desarrollo de Flask:

    ```Terminal
        gunicorn app:app```

La aplicación estará disponible en http://127.0.0.1:5000.

