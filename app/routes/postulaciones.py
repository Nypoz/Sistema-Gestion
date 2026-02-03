from flask import Blueprint, request, redirect, url_for, flash, render_template
from app import db
from app.models import Postulacion, EstadoPostulacion
from app.services.postulacion_service import PostulacionService

bp = Blueprint('postulaciones', __name__, url_prefix='/postulaciones')


@bp.route('/crear', methods=['POST'])
def crear():
    """Crear una nueva postulación."""
    postulante_id = request.form.get('postulante_id')
    puesto_id = request.form.get('puesto_id')

    if not postulante_id or not puesto_id:
        flash('Datos incompletos', 'error')
        return redirect(request.referrer or url_for('main.index'))

    try:
        postulacion = PostulacionService.crear_postulacion(
            int(postulante_id),
            int(puesto_id)
        )
        flash('Postulación creada exitosamente', 'success')

        # Redirigir según de dónde vino
        if 'desde_puesto' in request.form:
            return redirect(url_for('puestos.ver', id=puesto_id))
        else:
            return redirect(url_for('postulantes.ver', id=postulante_id))

    except ValueError as e:
        flash(str(e), 'error')
        return redirect(request.referrer or url_for('main.index'))


@bp.route('/<int:id>/estado', methods=['POST'])
def cambiar_estado(id):
    """Cambiar estado de una postulación."""
    nuevo_estado = request.form.get('estado')

    try:
        PostulacionService.cambiar_estado(id, nuevo_estado)
        flash('Estado actualizado', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')

    return redirect(request.referrer or url_for('main.index'))


@bp.route('/<int:id>/notas', methods=['POST'])
def actualizar_notas(id):
    """Actualizar notas de una postulación."""
    postulacion = Postulacion.query.get_or_404(id)
    postulacion.notas = request.form.get('notas', '')
    db.session.commit()

    flash('Notas actualizadas', 'success')
    return redirect(request.referrer or url_for('main.index'))


@bp.route('/<int:id>')
def ver(id):
    """Ver detalle de una postulación."""
    postulacion = Postulacion.query.get_or_404(id)
    return render_template('postulaciones/ver.html',
                           postulacion=postulacion,
                           estados=EstadoPostulacion)


@bp.route('/<int:id>/eliminar', methods=['POST'])
def eliminar(id):
    """Eliminar una postulación."""
    postulacion = Postulacion.query.get_or_404(id)
    puesto_id = postulacion.puesto_id

    db.session.delete(postulacion)
    db.session.commit()

    flash('Postulación eliminada', 'success')
    return redirect(url_for('puestos.ver', id=puesto_id))
