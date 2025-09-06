# tasks.py
from celery import Celery
from flask_mail import Mail, Message
from models import User
from app import app  # Importamos la instancia 'app' de Flask desde app.py

# Creamos una instancia de Mail, asociándola con la configuración de nuestra app Flask
mail = Mail(app)

def make_celery(app_instance):
    """
    Esta función de fábrica crea y configura una instancia de Celery
    para que funcione correctamente con el contexto de la aplicación Flask.
    """
    celery = Celery(
        app_instance.import_name,
        backend=app_instance.config['CELERY_RESULT_BACKEND'],
        broker=app_instance.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app_instance.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app_instance.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

# Creamos la instancia de Celery que será usada por el worker y por nuestra app
celery = make_celery(app)


@celery.task
def send_email_notification(patient_username):
    """
    Tarea en segundo plano para enviar un email de notificación.
    """
    try:
        # En una app real, aquí tendrías una lógica para asignar a un psicólogo disponible.
        # Para este demo, notificaremos al primer psicólogo que encontremos en la BD.
        psychologist = User.query.filter_by(role='psychologist').first()

        if psychologist:
            # Para este demo, asumimos que el username del psicólogo es un email válido.
            # En un sistema real, el modelo User tendría un campo 'email'.
            recipient_email = "edgaytanc@gmail.com"  # <-- CAMBIA ESTO A TU EMAIL PARA PROBAR
            
            subject = f"[Equilibra] Nuevo Caso Requiere Revisión: {patient_username}"
            body = f"""
            Hola Dr./Dra. {psychologist.username},

            El sistema ha detectado que el paciente '{patient_username}' ha sido marcado automáticamente para revisión.

            Por favor, inicia sesión en tu dashboard para ver los detalles de la conversación.

            Gracias,
            Sistema de Alertas de Equilibra
            """
            
            msg = Message(subject, recipients=[recipient_email], body=body)
            mail.send(msg)
            print(f"Email de notificación enviado a {recipient_email} sobre el caso {patient_username}")
            return f"Email enviado a {recipient_email}"
        else:
            print("No se encontraron psicólogos para notificar.")
            return "No se encontraron psicólogos."
    except Exception as e:
        print(f"Error al enviar email: {e}")
        # Hacemos un reintento si la tarea falla, con un delay de 60 segundos
        raise send_email_notification.retry(exc=e, countdown=60)
