# auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from models import db, User
from flask_login import login_user, logout_user, login_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        email = request.form.get('email')

        user = User.query.filter_by(username=username).first()
        if user:
            flash('El nombre de usuario ya existe.')
            return redirect(url_for('auth.register'))
        
        # --- NUEVA LÍNEA (comprobación de email) ---
        email_exists = User.query.filter_by(email=email).first()
        if email_exists:
            flash('El correo electrónico ya está registrado.')
            return redirect(url_for('auth.register'))

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()

        flash('¡Registro exitoso! Por favor, inicia sesión.')
        return redirect(url_for('auth.login'))
        
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            flash('Por favor, verifica tus datos de inicio de sesión y vuelve a intentarlo.')
            return redirect(url_for('auth.login'))
        
        login_user(user)
        return redirect(url_for('main.chat_page'))

    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))