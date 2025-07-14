# app.py
import os
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template, Blueprint, redirect, url_for
from transformers import pipeline
from flask_login import LoginManager, login_required, current_user
from flask_migrate import Migrate

# Importar modelos y blueprints
from models import db, User, Message
from auth import auth_bp

# --- CONFIGURACIÓN DE LA APP ---
app = Flask(__name__)
# Necesitas una clave secreta para las sesiones de usuario
app.config['SECRET_KEY'] = 'una-clave-secreta-muy-dificil-de-adivinar'
# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chatbot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- INICIALIZACIÓN DE EXTENSIONES ---
db.init_app(app)
migrate = Migrate(app, db) # Para gestionar cambios en la BD

login_manager = LoginManager()
login_manager.login_view = 'auth.login' # Página a la que se redirige si no se ha iniciado sesión
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- CARGA DE MODELOS DE IA (igual que antes) ---
print("Cargando el modelo de detección de sentimientos...")
detector = pipeline('sentiment-analysis', model='pysentimiento/robertuito-sentiment-analysis')
print("Modelo cargado.")

try:
    genai.configure(api_key="AIzaSyBm_devxD8dMh29wTWaZ2D5Qnig4hQIeN8") # <-- REEMPLAZA ESTO
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
    # ----------------------------------------------------
    user_message_content = request.json.get("message")
    if not user_message_content:
        return jsonify({"error": "No se recibió ningún mensaje."}), 400

    # Creamos el objeto Message para el usuario y lo añadimos a la sesión de la BD
    user_message = Message(content=user_message_content, sender='user', author=current_user)
    db.session.add(user_message)


    # 2. DETECCIÓN DE ANSIEDAD/NEGATIVIDAD
    # ----------------------------------------------------
    detection_result = detector(user_message_content)[0]
    anxiety_score = detection_result['score'] if detection_result['label'] == 'NEG' else 0.0


    # 3. GENERACIÓN DE LA RESPUESTA DEL CHATBOT (GEMINI)
    # ----------------------------------------------------
    bot_response_text = "Lo siento, estoy teniendo problemas para conectar en este momento. Por favor, intenta de nuevo más tarde."
    if model_gemini:
      try:
          # El prompt de sistema le da la personalidad y las reglas a la IA
          full_prompt = SYSTEM_PROMPT + f"\n\nUsuario: {user_message_content}\nKai:"
          response = model_gemini.generate_content(full_prompt)
          bot_response_text = response.text
      except Exception as e:
          print(f"Error al generar respuesta de Gemini: {e}")
          # El mensaje de error por defecto ya está asignado arriba

    # Creamos el objeto Message para la respuesta del bot
    bot_message = Message(content=bot_response_text, sender='bot', author=current_user)
    db.session.add(bot_message)


    # 4. LÓGICA DE REMISIÓN AUTOMÁTICA
    # ----------------------------------------------------
    # Solo se aplica a usuarios con rol 'paciente' y que no hayan sido marcados previamente
    if current_user.role == 'patient' and current_user.status == 'active':
        # Obtenemos los últimos 10 mensajes del usuario para tener contexto
        last_user_messages = Message.query.filter_by(user_id=current_user.id, sender='user').order_by(Message.timestamp.desc()).limit(10).all()
        
        # Evaluamos si el usuario tiene un historial mínimo de 5 mensajes
        if len(last_user_messages) >= 5:
            negative_count = 0
            # Contamos cuántos de esos mensajes tienen un alto sentimiento negativo
            for msg in last_user_messages:
                score = detector(msg.content)[0]
                # Usamos un umbral para considerar un mensaje como "muy negativo"
                if score['label'] == 'NEG' and score['score'] > 0.7:
                    negative_count += 1
            
            # Si 3 o más de los últimos mensajes son muy negativos, marcamos al usuario
            if negative_count >= 3:
                current_user.status = 'requires_review'
                print(f"ATENCIÓN: Usuario '{current_user.username}' ha sido marcado para revisión.")


    # 5. GUARDAR CAMBIOS Y DEVOLVER RESPUESTA
    # ----------------------------------------------------
    # Con un solo commit, guardamos el mensaje del usuario, el del bot y el posible cambio de estado
    db.session.commit()

    # Devolvemos la respuesta al frontend en formato JSON
    return jsonify({
        "bot_response": bot_response_text,
        "anxiety_score": f"{anxiety_score:.2f}"
    })

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Seguridad: Solo los psicólogos pueden ver esta página
    if current_user.role != 'psychologist':
        flash('Acceso no autorizado.')
        return redirect(url_for('main.chat_page'))
    
    # Buscamos a todos los pacientes que necesitan revisión
    flagged_users = User.query.filter_by(role='patient', status='requires_review').all()
    
    return render_template('dashboard.html', users=flagged_users)


@main_bp.route('/case/<int:user_id>')
@login_required
def view_case(user_id):
    # Seguridad: Solo los psicólogos pueden ver casos
    if current_user.role != 'psychologist':
        flash('Acceso no autorizado.')
        return redirect(url_for('main.chat_page'))
        
    # Obtenemos al paciente y sus mensajes
    patient = User.query.get_or_404(user_id)
    messages = Message.query.filter_by(user_id=patient.id).order_by(Message.timestamp.asc()).all()
    
    return render_template('view_case.html', patient=patient, messages=messages)

# Registrar los Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5000)