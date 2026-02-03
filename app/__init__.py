from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
import os

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Iniciá sesión para acceder al panel de administración'
login_manager.login_message_category = 'warning'


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Asegurar que existe la carpeta de uploads
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import Usuario
        return Usuario.query.get(int(user_id))

    from app.routes import main, puestos, postulantes, postulaciones, public, auth

    # Rutas públicas (landing, vacantes, autopostulación)
    app.register_blueprint(public.bp)

    # Rutas de autenticación
    app.register_blueprint(auth.bp)

    # Rutas admin (bajo /admin) - protegidas con @login_required
    app.register_blueprint(main.bp, url_prefix='/admin')
    app.register_blueprint(puestos.bp, url_prefix='/admin/puestos')
    app.register_blueprint(postulantes.bp, url_prefix='/admin/postulantes')
    app.register_blueprint(postulaciones.bp, url_prefix='/admin/postulaciones')

    with app.app_context():
        db.create_all()
        # Crear usuario admin por defecto si no existe
        _create_default_admin()

    return app


def _create_default_admin():
    from app.models import Usuario
    if not Usuario.query.filter_by(email='carolina@lasteniahr.com').first():
        admin = Usuario(
            email='carolina@lasteniahr.com',
            nombre='Carolina'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
