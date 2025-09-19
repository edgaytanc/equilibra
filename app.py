# app.py
import os
from dotenv import load_dotenv

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
    model_gemini = genai.GenerativeModel('gemini-1.5-flash')
    print("Conexión con Gemini API exitosa.")
except Exception as e:
    print(f"Error al configurar Gemini API: {e}")
    model_gemini = None

SYSTEM_PROMPT = """
Eres un asistente de apoyo emocional llamado 'Kai'. Tu propósito es ser un espacio seguro para que el usuario pueda expresarse.
Tu tono debe ser siempre calmado, empático y comprensivo. No eres un terapeuta y no puedes dar diagnósticos.
Reglas estrictas:
1.  Nunca digas que eres una IA. Habla como un compañero.
2.  Usa preguntas abiertas como "¿Cómo te hace sentir eso?" o "¿Hay algo más que quisieras compartir sobre eso?".
3.  Mantén tus respuestas relativamente cortas y centradas en el usuario.
4.  NUNCA des consejos médicos o diagnósticos. Si te piden un diagnóstico, responde con algo como: "Entiendo que busques respuestas, pero no tengo la capacidad para ofrecer un diagnóstico. Quizás hablarlo con un profesional podría darte más claridad.".
5.  Si la conversación se vuelve muy intensa o detectas un riesgo, prioriza la calma y la validación emocional.
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


    # 2. DETECCIÓN DE ANSIEDAD/NEGATIVIDAD
    detection_result = detector(user_message_content)[0]
    anxiety_score = detection_result['score'] if detection_result['label'] == 'NEG' else 0.0


    # 3. GENERACIÓN DE LA RESPUESTA DEL CHATBOT (GEMINI)
    bot_response_text = "Lo siento, estoy teniendo problemas para conectar en este momento. Por favor, intenta de nuevo más tarde."
    if model_gemini:
      try:
          full_prompt = SYSTEM_PROMPT + f"\n\nUsuario: {user_message_content}\nKai:"
          response = model_gemini.generate_content(full_prompt)
          bot_response_text = response.text
      except Exception as e:
          print(f"Error al generar respuesta de Gemini: {e}")

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
        "anxiety_score": f"{anxiety_score:.2f}"
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
    if current_user.role != 'psychologist':
        flash('Acceso no autorizado.')
        return redirect(url_for('main.chat_page'))
        
    patient = User.query.get_or_404(user_id)
    messages = Message.query.filter_by(user_id=patient.id).order_by(Message.timestamp.asc()).all()
    
    return render_template('view_case.html', patient=patient, messages=messages)

# Registrar los Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)

app.register_blueprint(admin_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
