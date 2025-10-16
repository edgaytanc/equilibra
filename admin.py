# admin.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from models import db, User
from flask_login import login_required, current_user
from functools import wraps

# 1. Creamos un decorador personalizado para proteger rutas
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Acceso no autorizado. Se requiere rol de administrador.', 'danger')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function

# 2. Creamos el Blueprint para las rutas de administración
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    # Mostramos una lista de todos los psicólogos registrados
    psychologists = User.query.filter_by(role='psychologist').all()
    return render_template('admin/dashboard.html', psychologists=psychologists)

@admin_bp.route('/add_psychologist', methods=['GET', 'POST'])
@login_required
@admin_required
def add_psychologist():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Verificamos si el usuario o el email ya existen
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            flash('El nombre de usuario o el email ya existen.', 'warning')
            return redirect(url_for('admin.add_psychologist'))

        # Creamos el nuevo usuario con el rol de psicólogo
        new_psychologist = User(
            username=username,
            email=email,
            role='psychologist'
        )
        new_psychologist.set_password(password)
        
        db.session.add(new_psychologist)
        db.session.commit()

        flash(f'Psicólogo "{username}" creado exitosamente.', 'success')
        return redirect(url_for('admin.dashboard'))
        
    return render_template('admin/add_psychologist.html')

# --- NUEVA RUTA PARA EDITAR PSICÓLOGOS ---
@admin_bp.route('/edit_psychologist/<int:psy_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_psychologist(psy_id):
    psychologist = User.query.get_or_404(psy_id)
    if psychologist.role != 'psychologist':
        flash('Este usuario no es un psicólogo.', 'danger')
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        new_username = request.form.get('username')
        new_email = request.form.get('email')

        # Verificar si el nuevo username o email ya están en uso por OTRO usuario
        if new_username != psychologist.username and User.query.filter_by(username=new_username).first():
            flash('El nuevo nombre de usuario ya está en uso.', 'warning')
            return render_template('admin/edit_psychologist.html', psychologist=psychologist)
        
        if new_email != psychologist.email and User.query.filter_by(email=new_email).first():
            flash('El nuevo correo electrónico ya está en uso.', 'warning')
            return render_template('admin/edit_psychologist.html', psychologist=psychologist)

        psychologist.username = new_username
        psychologist.email = new_email
        db.session.commit()
        flash(f'Datos del psicólogo "{psychologist.username}" actualizados correctamente.', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/edit_psychologist.html', psychologist=psychologist)

# --- NUEVA RUTA PARA ELIMINAR PSICÓLOGOS ---
@admin_bp.route('/delete_psychologist/<int:psy_id>', methods=['POST'])
@login_required
@admin_required
def delete_psychologist(psy_id):
    psychologist_to_delete = User.query.get_or_404(psy_id)
    if psychologist_to_delete.role != 'psychologist':
        flash('Este usuario no es un psicólogo.', 'danger')
        return redirect(url_for('admin.dashboard'))
        
    # Opcional: Reasignar pacientes antes de eliminar al psicólogo
    # for patient in psychologist_to_delete.assigned_patients:
    #     patient.assigned_psychologist_id = None
    #     db.session.add(patient)

    db.session.delete(psychologist_to_delete)
    db.session.commit()
    flash(f'El psicólogo "{psychologist_to_delete.username}" ha sido eliminado.', 'success')
    return redirect(url_for('admin.dashboard'))