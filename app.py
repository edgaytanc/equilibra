# app.py
import os
from dotenv import load_dotenv
import json
from models import db, User, Message
from auth import auth_bp

from admin import admin_bp

# Cargar las variables de entorno del archivo .env al inicio
load_dotenv()

import google.generativeai as genai
from flask import Flask, request, jsonify, render_template, Blueprint, redirect, url_for, flash
from transformers import pipeline
from flask_login import LoginManager, login_required, current_user
from flask_migrate import Migrate
from flask_mail import Mail

# Importar modelos y blueprints
from models import db, User, Message
from auth import auth_bp

# --- CONFIGURACIÓN DE LA APP ---
app = Flask(__name__)
# Usamos .from_mapping para cargar toda la configuración de una vez.
# Esto es más limpio y evita reescribir app.config.
app.config.from_mapping(
    SECRET_KEY = os.getenv('SECRET_KEY'),
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL'),
    SQLALCHEMY_TRACK_MODIFICATIONS = False,
    # Configuración para Celery (leída desde .env)
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL'),
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND'),
    # Configuración para Flask-Mail (leída desde .env)
    MAIL_SERVER = os.getenv('MAIL_SERVER'),
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587)),
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() in ['true', '1', 't'],
    MAIL_USERNAME = os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD'),
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
)


# --- INICIALIZACIÓN DE EXTENSIONES ---
db.init_app(app)
migrate = Migrate(app, db) # Para gestionar cambios en la BD
mail = Mail(app) # Inicializa Flask-Mail con la app

login_manager = LoginManager()
login_manager.login_view = 'auth.login' # Página a la que se redirige si no se ha iniciado sesión
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- CARGA DE MODELOS DE IA ---
print("Cargando el modelo de detección de sentimientos...")
detector = pipeline('sentiment-analysis', model='pysentimiento/robertuito-sentiment-analysis')
print("Modelo cargado.")

try:
    # Leemos la API key desde la variable de entorno
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    if not gemini_api_key:
        raise ValueError("No se encontró la API Key de Gemini en el archivo .env")
    genai.configure(api_key=gemini_api_key)
    model_gemini = genai.GenerativeModel('gemini-2.0-flash-exp')
    print("Conexión con Gemini API exitosa.")
except Exception as e:
    print(f"Error al configurar Gemini API: {e}")
    model_gemini = None

SYSTEM_PROMPT = """
Eres Elena, una compañera de apoyo emocional cálida, paciente y curiosa. Tu objetivo es crear un espacio seguro donde el usuario pueda explorar sus sentimientos.

Jamás menciones que eres una IA. No eres terapeuta, por lo que no diagnosticas ni das consejos médicos, legales o de medicación. Tu rol es escuchar, reflejar y ayudar a clarificar.

---
### Flujo de Conversación Dinámico:

**1. Inicio: Validar y Reflejar (Primeros 1-2 Mensajes)**
* Comienza validando la emoción del usuario. **No uses la misma frase de apertura cada vez.** Integra la validación de forma natural.
* Usa una pregunta abierta de la categoría "Profundizar en el Sentimiento" para entender el problema central.

**2. Desarrollo: Explorar y Conectar (A partir del 3er Mensaje)**
* **REGLA CLAVE: Después de 2 o 3 respuestas del usuario sobre el mismo problema, DEJA de preguntar "¿Qué es lo más difícil?".** Ya tienes el contexto.
* **Es el momento de cambiar de táctica. Pasa a las preguntas de las categorías "Conectar con Necesidades y Recursos" o "Explorar la Situación".**
* **Usa la Síntesis:** Cuando el usuario conecte varios problemas (ej. "el trabajo me causa ansiedad, lo que me impide trabajar, y eso significa que no tengo dinero para comida"), es tu señal para sintetizar. Refleja esa conexión para que el usuario se sienta comprendido en un nivel más profundo.
    * *Ejemplo de Síntesis:* "Entiendo. Es como una cadena muy pesada: la ansiedad por el trabajo acumulado te paraliza, la parálisis impide que te paguen, y la falta de pago crea una ansiedad aún más urgente por necesidades básicas como la comida. Suena como estar atrapado en un círculo vicioso muy angustiante."

**3. Madurez: Ofrecer Perspectiva (Solo si el usuario se siente atascado)**
* Si el usuario dice explícitamente "no sé qué hacer" o "estoy bloqueado", es tu oportunidad para ofrecer una "Micro-Sugerencia" colaborativa, siempre en forma de pregunta.

---
### Tu Banco de Herramientas Conversacionales:

**1. Validación Empática (Varía tus frases):**
* "Eso que describes suena increíblemente agotador/frustrante."
* "Tiene todo el sentido del mundo que te sientas así."
* "Me queda claro que estás lidiando con un peso muy grande."
* "Gracias por confiarme esto, noto la carga que llevas."

**2. Preguntas Abiertas (¡PROHIBIDO REPETIR LA MISMA CATEGORÍA SEGUIDA!):**

* **Categoría: Profundizar en el Sentimiento (Para el inicio)**
    * "¿Qué es lo más difícil de esa situación para ti?"
    * "Si pudieras ponerle un nombre a esa sensación, ¿cuál sería?"
    * "¿Qué pensamientos suelen acompañar a este sentimiento?"

* **Categoría: Conectar con Necesidades y Recursos (Para el desarrollo)**
    * "Frente a todo esto, ¿qué es lo que más necesitarías ahora mismo?"
    * "¿Qué te ha ayudado en el pasado, aunque sea un poco, cuando te has sentido así?"
    * "Si tuvieras una varita mágica, ¿cuál sería el primer pequeño cambio que harías?"
    * "Dejando de lado las soluciones por un momento, ¿qué te daría un respiro, aunque sea de 5 minutos?"

* **Categoría: Micro-Sugerencias Colaborativas (Para cuando se sientan atascados)**
    * "A veces, cuando la mente está tan saturada, enfocarse en lo más pequeño puede ayudar. ¿Qué pasaría si, en lugar de pensar en 'todo el trabajo', eligieras solo UNA tarea, la más pequeña, y la anotaras en un papel?"
    * "He escuchado que nombrar tres cosas que puedes ver o sentir a tu alrededor puede ayudar a calmar la ansiedad en el momento. ¿Te suena a algo que te gustaría intentar?"

---
### Reglas de Seguridad (Inquebrantables):

* **Riesgo Inminente (autolesión, suicidio, violencia):** Valida el dolor ("Escucho que estás en un lugar muy oscuro y doloroso") y deriva inmediatamente a ayuda profesional ("En momentos así, es fundamental hablar con alguien que pueda ofrecerte ayuda inmediata y especializada. Un profesional en una línea de crisis podría acompañarte mejor que yo en este momento.").
* **Petición de Consejos Directos:** Si te piden un diagnóstico o qué hacer, reafirma tu rol: *"Como compañera de apoyo, no tengo las herramientas para darte un consejo sobre eso, pero sí puedo ayudarte a explorar qué opciones sientes que tienes tú. ¿Te gustaría que lo hiciéramos?"*
"""

# --- BLUEPRINTS Y RUTAS PRINCIPALES ---
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('main.chat_page'))
    return redirect(url_for('auth.login'))

@main_bp.route('/chat_page')
@login_required
def chat_page():
    # Cargar el historial de chat del usuario actual
    past_messages = Message.query.filter_by(user_id=current_user.id).order_by(Message.timestamp.asc()).all()
    return render_template('index.html', messages=past_messages)

@main_bp.route('/chat', methods=['POST'])
@login_required
def chat():
    """
    Procesa el mensaje del usuario, obtiene una respuesta del bot,
    guarda ambos mensajes, ejecuta la lógica de remisión y devuelve
    la respuesta al frontend.
    """
    # 1. RECIBIR Y GUARDAR EL MENSAJE DEL USUARIO
    user_message_content = request.json.get("message")
    if not user_message_content:
        return jsonify({"error": "No se recibió ningún mensaje."}), 400

    user_message = Message(content=user_message_content, sender='user', author=current_user)
    db.session.add(user_message)


    # 2. DETECCIÓN DE SENTIMIENTO NEGATIVO
    detection_result = detector(user_message_content)[0]
    anxiety_score = detection_result['score'] if detection_result['label'] == 'NEG' else 0.0

    # --- INICIO: NUEVA LÓGICA PARA ETIQUETA DINÁMICA ---
    negativity_label = "Ansiedad"
    # Si la puntuación de negatividad es muy alta (ej. > 0.8), la consideramos "Estrés"
    if anxiety_score > 0.8:
        negativity_label = "Estrés"
    # --- FIN: NUEVA LÓGICA ---


    # 3. GENERACIÓN DE LA RESPUESTA DEL CHATBOT (GEMINI)
    bot_response_text = "Lo siento, estoy teniendo problemas para conectar en este momento. Por favor, intenta de nuevo más tarde."
    if model_gemini:
      try:
          full_prompt = SYSTEM_PROMPT + f"\n\nUsuario: {user_message_content}\nElena:"
          response = model_gemini.generate_content(full_prompt)
          # Agregamos una validación para asegurarnos de que la respuesta tiene contenido
          if response and response.text:
              bot_response_text = response.text
          else:
              # Si no hay texto, es posible que la respuesta haya sido bloqueada
              print("Advertencia: La respuesta de Gemini fue generada pero no contiene texto. Puede haber sido bloqueada por políticas de seguridad.")
              print(f"Prompt Feedback: {response.prompt_feedback}")
              bot_response_text = "No he podido procesar esa respuesta. ¿Podrías intentar reformular tu mensaje?"
      except Exception as e:
          # Imprimimos el error completo para poder diagnosticarlo
          print("="*30)
          print(f"ERROR AL LLAMAR A LA API DE GEMINI: {e}")
          print("="*30)

    bot_message = Message(content=bot_response_text, sender='bot', author=current_user)
    db.session.add(bot_message)


    # 4. LÓGICA DE REMISIÓN Y NOTIFICACIÓN
    if current_user.role == 'patient' and current_user.status == 'active':
        last_user_messages = Message.query.filter_by(user_id=current_user.id, sender='user').order_by(Message.timestamp.desc()).limit(10).all()
        
        if len(last_user_messages) >= 5:
            negative_count = 0
            for msg in last_user_messages:
                score = detector(msg.content)[0]
                if score['label'] == 'NEG' and score['score'] > 0.7:
                    negative_count += 1
            
            if negative_count >= 3:
                current_user.status = 'requires_review'
                print(f"ATENCIÓN: Usuario '{current_user.username}' ha sido marcado para revisión.")
                
                # --- INICIO: LLAMADA A LA TAREA ASÍNCRONA ---
                # Importamos la tarea aquí para evitar problemas de importación circular
                from tasks import assign_patient_and_notify
                # Usamos .delay() para poner la tarea en la cola de Redis sin bloquear la app
                assign_patient_and_notify.delay(patient_id=current_user.id)
                # --- FIN: LLAMADA A LA TAREA ASÍNCRONA ---

    # 5. GUARDAR CAMBIOS Y DEVOLVER RESPUESTA
    db.session.commit()

    return jsonify({
        "bot_response": bot_response_text,
        "anxiety_score": f"{anxiety_score:.2f}",
        "negativity_label": negativity_label  # <-- DATO ADICIONAL AÑADIDO
    })

@main_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'psychologist':
        flash('Acceso no autorizado.')
        return redirect(url_for('main.chat_page'))
    
    # --- LÓGICA MODIFICADA DEL DASHBOARD ---
    # Mostrar tanto los casos asignados a este psicólogo como los que no tienen asignación
    unassigned_users = User.query.filter_by(role='patient', status='requires_review').all()
    assigned_to_me = User.query.filter_by(assigned_psychologist_id=current_user.id).all()
    
    return render_template('dashboard.html', unassigned=unassigned_users, assigned=assigned_to_me)


@main_bp.route('/case/<int:user_id>')
@login_required
def view_case(user_id):
    if current_user.role not in ['psychologist', 'admin']:
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('main.chat_page'))
        
    patient = User.query.get_or_404(user_id)
    messages = Message.query.filter_by(user_id=patient.id).order_by(Message.timestamp.asc()).all()
    
    # --- INICIO: LÓGICA PARA PREPARAR DATOS DE LA GRÁFICA ---
    chart_labels = []
    chart_data = []

    # Iteramos solo sobre los mensajes del usuario para analizar su sentimiento
    user_messages = [msg for msg in messages if msg.sender == 'user']

    for msg in user_messages:
        # Formateamos la fecha para que sea legible en la gráfica
        chart_labels.append(msg.timestamp.strftime('%d/%m %H:%M'))
        
        # Analizamos el sentimiento de cada mensaje
        detection_result = detector(msg.content)[0]
        score = detection_result['score'] if detection_result['label'] == 'NEG' else 0.0
        chart_data.append(round(score, 2))
    # --- FIN: LÓGICA PARA PREPARAR DATOS DE LA GRÁFICA ---

    return render_template(
        'view_case.html', 
        patient=patient, 
        messages=messages,
        # Pasamos los datos a la plantilla de forma segura usando json.dumps
        chart_labels=json.dumps(chart_labels),
        chart_data=json.dumps(chart_data)
    )

# Registrar los Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)

app.register_blueprint(admin_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
