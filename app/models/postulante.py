from app import db
from datetime import datetime


class Postulante(db.Model):
    __tablename__ = 'postulantes'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    telefono = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # CV
    cv_filename = db.Column(db.String(300))
    cv_texto = db.Column(db.Text)  # texto extraído del CV

    # Perfil extraído del CV (cacheado)
    experiencia_detectada = db.Column(db.Integer)  # años
    tecnologias_detectadas = db.Column(db.String(500))
    nivel_ingles_detectado = db.Column(db.String(50))
    tiene_titulo_detectado = db.Column(db.Boolean)

    # Relaciones
    postulaciones = db.relationship('Postulacion', backref='postulante', lazy='dynamic')

    @property
    def nombre_completo(self):
        return f'{self.nombre} {self.apellido}'

    def get_tecnologias_detectadas_list(self):
        if not self.tecnologias_detectadas:
            return []
        return [t.strip().upper() for t in self.tecnologias_detectadas.split(',') if t.strip()]

    def __repr__(self):
        return f'<Postulante {self.nombre_completo}>'
