from app import db
from enum import Enum
from datetime import datetime


class NivelIngles(Enum):
    NO_REQUERIDO = 0
    BASICO = 1
    INTERMEDIO = 2
    AVANZADO = 3
    FLUIDO = 4

    def __str__(self):
        labels = {
            'NO_REQUERIDO': 'No requerido',
            'BASICO': 'Básico',
            'INTERMEDIO': 'Intermedio',
            'AVANZADO': 'Avanzado',
            'FLUIDO': 'Fluido/Nativo'
        }
        return labels.get(self.name, self.name)


class EstadoPuesto(Enum):
    ABIERTO = 'abierto'
    CERRADO = 'cerrado'
    PAUSADO = 'pausado'


class Puesto(db.Model):
    __tablename__ = 'puestos'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    empresa = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    estado = db.Column(db.Enum(EstadoPuesto), default=EstadoPuesto.ABIERTO)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Requisitos
    experiencia_minima = db.Column(db.Integer, default=0)  # años
    tecnologias = db.Column(db.String(500))  # separadas por coma
    nivel_ingles = db.Column(db.Enum(NivelIngles), default=NivelIngles.NO_REQUERIDO)
    requiere_titulo = db.Column(db.Boolean, default=False)
    ubicacion = db.Column(db.String(200))
    modalidad = db.Column(db.String(50))  # remoto, presencial, hibrido
    salario_min = db.Column(db.Integer)
    salario_max = db.Column(db.Integer)

    # Relaciones
    postulaciones = db.relationship('Postulacion', backref='puesto', lazy='dynamic')

    def get_tecnologias_list(self):
        if not self.tecnologias:
            return []
        return [t.strip().upper() for t in self.tecnologias.split(',') if t.strip()]

    def set_tecnologias_list(self, tecnologias):
        self.tecnologias = ', '.join([t.strip().upper() for t in tecnologias])

    def __repr__(self):
        return f'<Puesto {self.titulo} @ {self.empresa}>'
