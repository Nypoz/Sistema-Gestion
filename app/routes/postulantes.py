from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_from_directory
from flask_login import login_required
from app import db
from app.models import Postulante, Puesto, EstadoPuesto
from app.services.postulacion_service import PostulacionService
import os

bp = Blueprint('postulantes', __name__)


# Proteger todas las rutas de este blueprint
@bp.before_request
@login_required
def require_login():
    pass


def allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@bp.route('/')
def listar():
    """Lista todos los postulantes."""
    buscar = request.args.get('buscar', '')

    if buscar:
        postulantes = Postulante.query.filter(
            (Postulante.nombre.ilike(f'%{buscar}%')) |
            (Postulante.apellido.ilike(f'%{buscar}%')) |
            (Postulante.email.ilike(f'%{buscar}%'))
        ).order_by(Postulante.created_at.desc()).all()
    else:
        postulantes = Postulante.query.order_by(Postulante.created_at.desc()).all()

    return render_template('postulantes/listar.html',
                           postulantes=postulantes,
                           buscar=buscar)


@bp.route('/nuevo', methods=['GET', 'POST'])
def nuevo():
    """Crear un nuevo postulante con CV."""
    if request.method == 'POST':
        # Verificar email único
        email = request.form['email']
        existente = Postulante.query.filter_by(email=email).first()
        if existente:
            flash('Ya existe un postulante con ese email', 'error')
            return render_template('postulantes/form.html', postulante=None)

        postulante = Postulante(
            nombre=request.form['nombre'],
            apellido=request.form['apellido'],
            email=email,
            telefono=request.form.get('telefono', ''),
        )

        db.session.add(postulante)
        db.session.commit()

        # Procesar CV si se subió
        if 'cv' in request.files:
            archivo = request.files['cv']
            if archivo and archivo.filename and allowed_file(archivo.filename):
                PostulacionService.procesar_cv(postulante, archivo=archivo)
                flash('CV procesado correctamente', 'success')
            elif archivo.filename:
                flash('Formato de archivo no permitido. Use PDF o DOCX', 'warning')

        flash('Postulante creado exitosamente', 'success')
        return redirect(url_for('postulantes.ver', id=postulante.id))

    return render_template('postulantes/form.html', postulante=None)


@bp.route('/<int:id>')
def ver(id):
    """Ver detalle de un postulante."""
    postulante = Postulante.query.get_or_404(id)
    postulaciones = postulante.postulaciones.order_by(Postulacion.created_at.desc()).all()

    # Puestos disponibles para postular
    puestos_disponibles = Puesto.query.filter_by(estado=EstadoPuesto.ABIERTO).all()
    # Filtrar los que ya postuló
    puestos_postulados = {p.puesto_id for p in postulaciones}
    puestos_disponibles = [p for p in puestos_disponibles if p.id not in puestos_postulados]

    return render_template('postulantes/ver.html',
                           postulante=postulante,
                           postulaciones=postulaciones,
                           puestos_disponibles=puestos_disponibles)


@bp.route('/<int:id>/editar', methods=['GET', 'POST'])
def editar(id):
    """Editar un postulante."""
    postulante = Postulante.query.get_or_404(id)

    if request.method == 'POST':
        # Verificar email único (excepto el actual)
        email = request.form['email']
        existente = Postulante.query.filter(
            Postulante.email == email,
            Postulante.id != id
        ).first()
        if existente:
            flash('Ya existe otro postulante con ese email', 'error')
            return render_template('postulantes/form.html', postulante=postulante)

        postulante.nombre = request.form['nombre']
        postulante.apellido = request.form['apellido']
        postulante.email = email
        postulante.telefono = request.form.get('telefono', '')

        # Procesar nuevo CV si se subió
        if 'cv' in request.files:
            archivo = request.files['cv']
            if archivo and archivo.filename and allowed_file(archivo.filename):
                PostulacionService.procesar_cv(postulante, archivo=archivo)
                flash('CV actualizado y procesado', 'success')

        db.session.commit()
        flash('Postulante actualizado', 'success')
        return redirect(url_for('postulantes.ver', id=postulante.id))

    return render_template('postulantes/form.html', postulante=postulante)


@bp.route('/<int:id>/cv')
def descargar_cv(id):
    """Descargar el CV de un postulante."""
    postulante = Postulante.query.get_or_404(id)

    if not postulante.cv_filename:
        flash('Este postulante no tiene CV cargado', 'warning')
        return redirect(url_for('postulantes.ver', id=id))

    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'],
        postulante.cv_filename,
        as_attachment=True
    )


@bp.route('/<int:id>/eliminar', methods=['POST'])
def eliminar(id):
    """Eliminar un postulante."""
    postulante = Postulante.query.get_or_404(id)

    # Eliminar archivo CV si existe
    if postulante.cv_filename:
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], postulante.cv_filename)
        if os.path.exists(filepath):
            os.remove(filepath)

    # Eliminar postulaciones asociadas
    for postulacion in postulante.postulaciones:
        db.session.delete(postulacion)

    db.session.delete(postulante)
    db.session.commit()

    flash('Postulante eliminado', 'success')
    return redirect(url_for('postulantes.listar'))


# Import Postulacion for the ver route
from app.models import Postulacion
