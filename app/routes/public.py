from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from app import db
from app.models import Puesto, Postulante, Postulacion, EstadoPuesto
from app.services.postulacion_service import PostulacionService

bp = Blueprint('public', __name__)


def allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@bp.route('/')
def landing():
    """Landing page pública de la consultora."""
    puestos_abiertos = Puesto.query.filter_by(estado=EstadoPuesto.ABIERTO).count()
    puestos_destacados = Puesto.query.filter_by(estado=EstadoPuesto.ABIERTO).order_by(Puesto.created_at.desc()).limit(3).all()
    return render_template('public/landing.html',
                           puestos_abiertos=puestos_abiertos,
                           puestos_destacados=puestos_destacados)


@bp.route('/vacantes')
def vacantes():
    """Lista de vacantes disponibles para postularse."""
    puestos = Puesto.query.filter_by(estado=EstadoPuesto.ABIERTO).order_by(Puesto.created_at.desc()).all()
    return render_template('public/vacantes.html', puestos=puestos)


@bp.route('/vacantes/<int:id>')
def vacante_detalle(id):
    """Detalle de una vacante con formulario de postulación."""
    puesto = Puesto.query.get_or_404(id)

    # Solo mostrar si está abierto
    if puesto.estado != EstadoPuesto.ABIERTO:
        flash('Esta vacante ya no está disponible', 'warning')
        return redirect(url_for('public.vacantes'))

    return render_template('public/vacante_detalle.html', puesto=puesto)


@bp.route('/postularme/<int:puesto_id>', methods=['POST'])
def postularme(puesto_id):
    """Procesa la autopostulación de un candidato."""
    puesto = Puesto.query.get_or_404(puesto_id)

    if puesto.estado != EstadoPuesto.ABIERTO:
        flash('Esta vacante ya no está disponible', 'error')
        return redirect(url_for('public.vacantes'))

    # Obtener datos del formulario
    nombre = request.form.get('nombre', '').strip()
    apellido = request.form.get('apellido', '').strip()
    email = request.form.get('email', '').strip().lower()
    telefono = request.form.get('telefono', '').strip()

    # Validaciones básicas
    if not nombre or not apellido or not email:
        flash('Por favor completá todos los campos obligatorios', 'error')
        return redirect(url_for('public.vacante_detalle', id=puesto_id))

    # Verificar si ya existe el postulante por email
    postulante = Postulante.query.filter_by(email=email).first()

    if postulante:
        # Verificar si ya postuló a este puesto
        postulacion_existente = Postulacion.query.filter_by(
            postulante_id=postulante.id,
            puesto_id=puesto_id
        ).first()

        if postulacion_existente:
            flash('Ya te postulaste a esta vacante anteriormente', 'warning')
            return redirect(url_for('public.vacante_detalle', id=puesto_id))

        # Actualizar datos si cambió algo
        postulante.nombre = nombre
        postulante.apellido = apellido
        postulante.telefono = telefono
    else:
        # Crear nuevo postulante
        postulante = Postulante(
            nombre=nombre,
            apellido=apellido,
            email=email,
            telefono=telefono
        )
        db.session.add(postulante)
        db.session.commit()

    # Procesar CV si se subió
    if 'cv' in request.files:
        archivo = request.files['cv']
        if archivo and archivo.filename and allowed_file(archivo.filename):
            PostulacionService.procesar_cv(postulante, archivo=archivo)
        elif archivo.filename:
            flash('Formato de CV no válido. Usá PDF o DOCX', 'warning')

    # Crear la postulación
    try:
        PostulacionService.crear_postulacion(postulante.id, puesto_id)
        flash('¡Tu postulación fue enviada exitosamente! Te contactaremos pronto.', 'success')
        return redirect(url_for('public.postulacion_exitosa'))
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('public.vacante_detalle', id=puesto_id))


@bp.route('/postulacion-exitosa')
def postulacion_exitosa():
    """Página de confirmación después de postularse."""
    return render_template('public/postulacion_exitosa.html')
