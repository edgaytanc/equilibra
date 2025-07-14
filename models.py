# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    # --- NUEVAS LÍNEAS ---
    # Rol del usuario: 'patient' o 'psychologist'
    role = db.Column(db.String(50), nullable=False, default='patient')
    # Estado del paciente para el sistema de triaje
    status = db.Column(db.String(50), nullable=False, default='active') 
    # 'active': estado normal
    # 'requires_review': marcado por la IA
    # 'assigned': un psicólogo está a cargo
    # --------------------
    
    messages = db.relationship('Message', backref='author', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    sender = db.Column(db.String(10), nullable=False) # 'user' o 'bot'
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)