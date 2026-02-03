from app import db
from enum import Enum
from datetime import datetime


class EstadoPostulacion(Enum):
    PENDIENTE = 'pendiente'
    EN_REVISION = 'en_revision'
    ENTREVISTA = 'entrevista'
    APROBADO = 'aprobado'
    RECHAZADO = 'rechazado'

    def __str__(self):
        labels = {
            'PENDIENTE': 'Pendiente',
            'EN_REVISION': 'En revisión',
            'ENTREVISTA': 'Entrevista',
            'APROBADO': 'Aprobado',
            'RECHAZADO': 'Rechazado'
        }
        return labels.get(self.name, self.name)


class Postulacion(db.Model):
    __tablename__ = 'postulaciones'

    id = db.Column(db.Integer, primary_key=True)
    postulante_id = db.Column(db.Integer, db.ForeignKey('postulantes.id'), nullable=False)
    puesto_id = db.Column(db.Integer, db.ForeignKey('puestos.id'), nullable=False)
    estado = db.Column(db.Enum(EstadoPostulacion), default=EstadoPostulacion.PENDIENTE)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Evaluación
    cumple_requisitos = db.Column(db.Boolean)
    puntaje = db.Column(db.Integer)  # 0-100
    notas = db.Column(db.Text)

    # Constraint único: un postulante no puede aplicar dos veces al mismo puesto
    __table_args__ = (
        db.UniqueConstraint('postulante_id', 'puesto_id', name='unique_postulacion'),
    )

    def pasar_a_revision(self):
        if self.estado == EstadoPostulacion.PENDIENTE:
            self.estado = EstadoPostulacion.EN_REVISION

    def pasar_a_entrevista(self):
        if self.estado == EstadoPostulacion.EN_REVISION:
            self.estado = EstadoPostulacion.ENTREVISTA

    def aprobar(self):
        self.estado = EstadoPostulacion.APROBADO

    def rechazar(self):
        self.estado = EstadoPostulacion.RECHAZADO

    def __repr__(self):
        return f'<Postulacion {self.postulante.nombre_completo} -> {self.puesto.titulo}>'
