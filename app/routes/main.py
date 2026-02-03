from flask import Blueprint, render_template
from flask_login import login_required
from app.models import Puesto, Postulante, Postulacion, EstadoPuesto

bp = Blueprint('main', __name__)


@bp.route('/')
@login_required
def index():
    """Dashboard principal."""
    puestos_abiertos = Puesto.query.filter_by(estado=EstadoPuesto.ABIERTO).count()
    total_postulantes = Postulante.query.count()
    total_postulaciones = Postulacion.query.count()

    # Últimas postulaciones
    ultimas_postulaciones = Postulacion.query.order_by(
        Postulacion.created_at.desc()
    ).limit(5).all()

    # Puestos con más postulaciones
    puestos_populares = Puesto.query.filter_by(estado=EstadoPuesto.ABIERTO).all()
    puestos_populares = sorted(
        puestos_populares,
        key=lambda p: p.postulaciones.count(),
        reverse=True
    )[:5]

    return render_template('index.html',
                           puestos_abiertos=puestos_abiertos,
                           total_postulantes=total_postulantes,
                           total_postulaciones=total_postulaciones,
                           ultimas_postulaciones=ultimas_postulaciones,
                           puestos_populares=puestos_populares)
