from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Puesto, Postulacion, NivelIngles, EstadoPuesto, EstadoPostulacion
from app.services.postulacion_service import PostulacionService

bp = Blueprint('puestos', __name__, url_prefix='/puestos')


@bp.route('/')
def listar():
    """Lista todos los puestos."""
    estado_filtro = request.args.get('estado', 'todos')

    if estado_filtro == 'todos':
        puestos = Puesto.query.order_by(Puesto.created_at.desc()).all()
    else:
        try:
            estado = EstadoPuesto(estado_filtro)
            puestos = Puesto.query.filter_by(estado=estado).order_by(Puesto.created_at.desc()).all()
        except ValueError:
            puestos = Puesto.query.order_by(Puesto.created_at.desc()).all()

    return render_template('puestos/listar.html',
                           puestos=puestos,
                           estados=EstadoPuesto,
                           estado_actual=estado_filtro)


@bp.route('/nuevo', methods=['GET', 'POST'])
def nuevo():
    """Crear un nuevo puesto."""
    if request.method == 'POST':
        puesto = Puesto(
            titulo=request.form['titulo'],
            empresa=request.form['empresa'],
            descripcion=request.form.get('descripcion', ''),
            experiencia_minima=int(request.form.get('experiencia_minima', 0)),
            tecnologias=request.form.get('tecnologias', ''),
            nivel_ingles=NivelIngles[request.form.get('nivel_ingles', 'NO_REQUERIDO')],
            requiere_titulo=request.form.get('requiere_titulo') == 'on',
            ubicacion=request.form.get('ubicacion', ''),
            modalidad=request.form.get('modalidad', ''),
            salario_min=int(request.form['salario_min']) if request.form.get('salario_min') else None,
            salario_max=int(request.form['salario_max']) if request.form.get('salario_max') else None,
        )

        db.session.add(puesto)
        db.session.commit()

        flash('Puesto creado exitosamente', 'success')
        return redirect(url_for('puestos.ver', id=puesto.id))

    return render_template('puestos/form.html',
                           puesto=None,
                           niveles_ingles=NivelIngles)


@bp.route('/<int:id>')
def ver(id):
    """Ver detalle de un puesto con sus postulaciones."""
    puesto = Puesto.query.get_or_404(id)

    # Filtros
    filtro_cumple = request.args.get('cumple', 'todos')
    filtro_estado = request.args.get('estado', 'todos')

    query = puesto.postulaciones

    if filtro_cumple == 'si':
        query = query.filter_by(cumple_requisitos=True)
    elif filtro_cumple == 'no':
        query = query.filter_by(cumple_requisitos=False)

    if filtro_estado != 'todos':
        try:
            estado = EstadoPostulacion(filtro_estado)
            query = query.filter_by(estado=estado)
        except ValueError:
            pass

    postulaciones = query.order_by(Postulacion.puntaje.desc()).all()
    stats = PostulacionService.obtener_estadisticas(id)

    return render_template('puestos/ver.html',
                           puesto=puesto,
                           postulaciones=postulaciones,
                           stats=stats,
                           estados=EstadoPostulacion,
                           filtro_cumple=filtro_cumple,
                           filtro_estado=filtro_estado)


@bp.route('/<int:id>/editar', methods=['GET', 'POST'])
def editar(id):
    """Editar un puesto existente."""
    puesto = Puesto.query.get_or_404(id)

    if request.method == 'POST':
        puesto.titulo = request.form['titulo']
        puesto.empresa = request.form['empresa']
        puesto.descripcion = request.form.get('descripcion', '')
        puesto.experiencia_minima = int(request.form.get('experiencia_minima', 0))
        puesto.tecnologias = request.form.get('tecnologias', '')
        puesto.nivel_ingles = NivelIngles[request.form.get('nivel_ingles', 'NO_REQUERIDO')]
        puesto.requiere_titulo = request.form.get('requiere_titulo') == 'on'
        puesto.ubicacion = request.form.get('ubicacion', '')
        puesto.modalidad = request.form.get('modalidad', '')
        puesto.salario_min = int(request.form['salario_min']) if request.form.get('salario_min') else None
        puesto.salario_max = int(request.form['salario_max']) if request.form.get('salario_max') else None

        db.session.commit()

        flash('Puesto actualizado', 'success')
        return redirect(url_for('puestos.ver', id=puesto.id))

    return render_template('puestos/form.html',
                           puesto=puesto,
                           niveles_ingles=NivelIngles)


@bp.route('/<int:id>/estado', methods=['POST'])
def cambiar_estado(id):
    """Cambiar estado del puesto."""
    puesto = Puesto.query.get_or_404(id)
    nuevo_estado = request.form.get('estado')

    try:
        puesto.estado = EstadoPuesto(nuevo_estado)
        db.session.commit()
        flash('Estado del puesto actualizado', 'success')
    except ValueError:
        flash('Estado inválido', 'error')

    return redirect(url_for('puestos.ver', id=id))


@bp.route('/<int:id>/eliminar', methods=['POST'])
def eliminar(id):
    """Eliminar un puesto."""
    puesto = Puesto.query.get_or_404(id)

    # Eliminar postulaciones asociadas
    for postulacion in puesto.postulaciones:
        db.session.delete(postulacion)

    db.session.delete(puesto)
    db.session.commit()

    flash('Puesto eliminado', 'success')
    return redirect(url_for('puestos.listar'))
