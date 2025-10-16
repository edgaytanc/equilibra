# seed.py
import os
from app import app, db
from models import User

def create_admin():
    """Crea el usuario administrador si no existe."""
    # Usamos el contexto de la aplicación para interactuar con la BD
    with app.app_context():
        # Lee las credenciales desde las variables de entorno
        admin_username = os.getenv('ADMIN_USERNAME', 'admin')
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@equilibra.com')
        admin_password = os.getenv('ADMIN_PASSWORD')

        if not admin_password:
            print("Error: La variable de entorno ADMIN_PASSWORD no está configurada.")
            return

        # Comprueba si el usuario o el email ya existen
        if User.query.filter_by(username=admin_username).first() is None and \
           User.query.filter_by(email=admin_email).first() is None:
            
            print(f"Creando usuario administrador: {admin_username}")
            
            admin_user = User(
                username=admin_username,
                email=admin_email,
                role='admin'
            )
            admin_user.set_password(admin_password)
            
            db.session.add(admin_user)
            db.session.commit()
            print("Usuario administrador creado exitosamente.")
        else:
            print("El usuario administrador ya existe.")

if __name__ == '__main__':
    create_admin()