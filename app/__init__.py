from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
import os

db = SQLAlchemy()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Asegurar que existe la carpeta de uploads
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)

    from app.routes import main, puestos, postulantes, postulaciones
    app.register_blueprint(main.bp)
    app.register_blueprint(puestos.bp)
    app.register_blueprint(postulantes.bp)
    app.register_blueprint(postulaciones.bp)

    with app.app_context():
        db.create_all()

    return app
