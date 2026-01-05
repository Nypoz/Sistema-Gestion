package org.example.repo;

import org.example.model.EstadoPostulacion;
import org.example.model.Postulacion;

import java.util.List;

public interface PostulacionRepository extends Repository<Postulacion> {
    boolean existsByPostulanteIdAndPuestoId(long postulanteId, long puestoId);

    List<Postulacion> findByEstado(EstadoPostulacion estado);
    List<Postulacion> findByPuestoNombre(String nombrePuesto);
    List<Postulacion> findByPuestoNombreAndEstado(String nombrePuesto, EstadoPostulacion estado);
}