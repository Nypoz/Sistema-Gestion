from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import Usuario
from datetime import datetime

bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and usuario.check_password(password):
            if not usuario.is_active:
                flash('Tu cuenta está desactivada. Contactá al administrador.', 'error')
                return render_template('auth/login.html')

            login_user(usuario, remember=remember)
            usuario.last_login = datetime.utcnow()
            db.session.commit()

            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.index'))
        else:
            flash('Email o contraseña incorrectos', 'error')

    return render_template('auth/login.html')


@bp.route('/logout')
@login_required
def logout():
    """Cerrar sesión."""
    logout_user()
    flash('Sesión cerrada correctamente', 'success')
    return redirect(url_for('public.landing'))
