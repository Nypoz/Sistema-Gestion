from app import db
from app.models import Postulante, Puesto, Postulacion, EstadoPostulacion, NivelIngles
from app.services.cv_parser import CVParser
import os
from werkzeug.utils import secure_filename
from flask import current_app


class PostulacionService:
    """Servicio para gestionar postulaciones y evaluación de candidatos."""

    NIVEL_INGLES_ORDEN = {
        None: 0,
        'NO_REQUERIDO': 0,
        'BASICO': 1,
        'INTERMEDIO': 2,
        'AVANZADO': 3,
        'FLUIDO': 4,
    }

    @classmethod
    def guardar_cv(cls, archivo):
        """Guarda un archivo CV y retorna el filename."""
        if not archivo:
            return None

        filename = secure_filename(archivo.filename)
        # Agregar timestamp para evitar colisiones
        import time
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{int(time.time())}{ext}"

        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        archivo.save(filepath)
        return filename

    @classmethod
    def procesar_cv(cls, postulante, archivo=None, filepath=None):
        """
        Procesa un CV y actualiza el perfil del postulante.

        Args:
            postulante: Instancia de Postulante
            archivo: FileStorage de werkzeug (upload)
            filepath: Ruta al archivo (si ya está guardado)
        """
        if archivo:
            filename = cls.guardar_cv(archivo)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            postulante.cv_filename = filename

        if filepath:
            perfil = CVParser.parsear(filepath=filepath)
        else:
            return

        postulante.cv_texto = perfil['texto_raw']
        postulante.experiencia_detectada = perfil['experiencia']
        postulante.tecnologias_detectadas = ', '.join(perfil['tecnologias'])
        postulante.nivel_ingles_detectado = perfil['nivel_ingles']
        postulante.tiene_titulo_detectado = perfil['tiene_titulo']

        db.session.commit()

    @classmethod
    def crear_postulacion(cls, postulante_id, puesto_id):
        """
        Crea una nueva postulación.

        Raises:
            ValueError si ya existe la postulación
        """
        existente = Postulacion.query.filter_by(
            postulante_id=postulante_id,
            puesto_id=puesto_id
        ).first()

        if existente:
            raise ValueError("El postulante ya aplicó a este puesto")

        postulacion = Postulacion(
            postulante_id=postulante_id,
            puesto_id=puesto_id
        )

        db.session.add(postulacion)
        db.session.flush()  # Para que se asignen las relaciones

        # Evaluar si cumple requisitos
        cls.evaluar_postulacion(postulacion)

        db.session.commit()
        return postulacion

    @classmethod
    def evaluar_postulacion(cls, postulacion):
        """Evalúa si una postulación cumple los requisitos del puesto."""
        postulante = Postulante.query.get(postulacion.postulante_id)
        puesto = Puesto.query.get(postulacion.puesto_id)

        puntaje = 0
        cumple = True
        notas = []

        # Evaluar experiencia
        exp_requerida = puesto.experiencia_minima or 0
        exp_candidato = postulante.experiencia_detectada or 0

        if exp_candidato >= exp_requerida:
            puntaje += 25
            if exp_candidato > exp_requerida:
                notas.append(f"✓ Experiencia: {exp_candidato} años (supera requisito de {exp_requerida})")
            else:
                notas.append(f"✓ Experiencia: {exp_candidato} años (cumple requisito)")
        else:
            cumple = False
            notas.append(f"✗ Experiencia: {exp_candidato} años (requiere {exp_requerida})")

        # Evaluar tecnologías
        techs_requeridas = set(puesto.get_tecnologias_list())
        techs_candidato = set(postulante.get_tecnologias_detectadas_list())

        if techs_requeridas:
            techs_match = techs_requeridas.intersection(techs_candidato)
            porcentaje_match = len(techs_match) / len(techs_requeridas) * 100

            if porcentaje_match >= 70:
                puntaje += 25
                notas.append(f"✓ Tecnologías: {len(techs_match)}/{len(techs_requeridas)} ({porcentaje_match:.0f}%)")
            elif porcentaje_match >= 50:
                puntaje += 15
                notas.append(f"~ Tecnologías: {len(techs_match)}/{len(techs_requeridas)} ({porcentaje_match:.0f}%)")
            else:
                cumple = False
                notas.append(f"✗ Tecnologías: {len(techs_match)}/{len(techs_requeridas)} ({porcentaje_match:.0f}%)")
        else:
            puntaje += 25
            notas.append("✓ Sin requisitos específicos de tecnología")

        # Evaluar nivel de inglés
        nivel_requerido = puesto.nivel_ingles
        nivel_candidato = postulante.nivel_ingles_detectado

        nivel_req_ord = cls.NIVEL_INGLES_ORDEN.get(nivel_requerido.name if nivel_requerido else None, 0)
        nivel_cand_ord = cls.NIVEL_INGLES_ORDEN.get(nivel_candidato, 0)

        if nivel_req_ord <= 0 or nivel_cand_ord >= nivel_req_ord:
            puntaje += 25
            if nivel_requerido and nivel_requerido != NivelIngles.NO_REQUERIDO:
                notas.append(f"✓ Inglés: {nivel_candidato or 'No detectado'} (requiere {nivel_requerido.name})")
            else:
                notas.append("✓ Inglés no requerido")
        else:
            cumple = False
            notas.append(f"✗ Inglés: {nivel_candidato or 'No detectado'} (requiere {nivel_requerido.name})")

        # Evaluar título universitario
        if puesto.requiere_titulo:
            if postulante.tiene_titulo_detectado:
                puntaje += 25
                notas.append("✓ Título universitario detectado")
            else:
                cumple = False
                notas.append("✗ No se detectó título universitario")
        else:
            puntaje += 25
            notas.append("✓ Título no requerido")

        postulacion.cumple_requisitos = cumple
        postulacion.puntaje = puntaje
        postulacion.notas = '\n'.join(notas)

    @classmethod
    def filtrar_por_requisitos(cls, puesto_id, solo_cumplen=True):
        """Filtra postulaciones según si cumplen requisitos."""
        query = Postulacion.query.filter_by(puesto_id=puesto_id)

        if solo_cumplen:
            query = query.filter_by(cumple_requisitos=True)

        return query.order_by(Postulacion.puntaje.desc()).all()

    @classmethod
    def filtrar_por_estado(cls, puesto_id, estado):
        """Filtra postulaciones por estado."""
        return Postulacion.query.filter_by(
            puesto_id=puesto_id,
            estado=estado
        ).order_by(Postulacion.puntaje.desc()).all()

    @classmethod
    def cambiar_estado(cls, postulacion_id, nuevo_estado):
        """Cambia el estado de una postulación."""
        postulacion = Postulacion.query.get_or_404(postulacion_id)
        postulacion.estado = EstadoPostulacion(nuevo_estado)
        db.session.commit()
        return postulacion

    @classmethod
    def obtener_estadisticas(cls, puesto_id):
        """Obtiene estadísticas de postulaciones para un puesto."""
        postulaciones = Postulacion.query.filter_by(puesto_id=puesto_id).all()

        stats = {
            'total': len(postulaciones),
            'cumplen_requisitos': sum(1 for p in postulaciones if p.cumple_requisitos),
            'por_estado': {},
            'puntaje_promedio': 0,
        }

        for estado in EstadoPostulacion:
            stats['por_estado'][estado.value] = sum(
                1 for p in postulaciones if p.estado == estado
            )

        if postulaciones:
            puntajes = [p.puntaje for p in postulaciones if p.puntaje]
            if puntajes:
                stats['puntaje_promedio'] = sum(puntajes) / len(puntajes)

        return stats
