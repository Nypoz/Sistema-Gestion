package org.example.repo;

import org.example.model.EstadoPostulacion;
import org.example.model.Postulacion;

import java.util.List;
import java.util.stream.Collectors;

public class InMemoryPostulacionRepository extends InMemoryRepository<Postulacion>
        implements PostulacionRepository {

    @Override
    public boolean existsByPostulanteIdAndPuestoId(long postulanteId, long puestoId) {
        return findAll().stream().anyMatch(p ->
                p.getPostulante().getId() == postulanteId &&
                        p.getPuesto().getId() == puestoId
        );
    }

    @Override
    public List<Postulacion> findByEstado(EstadoPostulacion estado) {
        return findAll().stream()
                .filter(p -> p.getEstado() == estado)
                .collect(Collectors.toList());
    }

    @Override
    public List<Postulacion> findByPuestoNombre(String nombrePuesto) {
        return findAll().stream()
                .filter(p -> p.getPuesto().getNombre().equalsIgnoreCase(nombrePuesto))
                .collect(Collectors.toList());
    }

    @Override
    public List<Postulacion> findByPuestoNombreAndEstado(String nombrePuesto, EstadoPostulacion estado) {
        return findAll().stream()
                .filter(p -> p.getPuesto().getNombre().equalsIgnoreCase(nombrePuesto))
                .filter(p -> p.getEstado() == estado)
                .collect(Collectors.toList());
    }
}