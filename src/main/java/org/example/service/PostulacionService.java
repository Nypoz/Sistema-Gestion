package org.example.service;

import org.example.model.*;
import org.example.repo.PostulacionRepository;

import java.util.List;
import java.util.Objects;

public class PostulacionService {

    private final PostulacionRepository repo;
    private final CVParser parser;

    public PostulacionService(PostulacionRepository repo, CVParser parser) {
        this.repo = Objects.requireNonNull(repo);
        this.parser = Objects.requireNonNull(parser);
    }

    public Postulacion crear(Postulante postulante, Puesto puesto) {
        Objects.requireNonNull(postulante);
        Objects.requireNonNull(puesto);

        if (repo.existsByPostulanteIdAndPuestoId(postulante.getId(), puesto.getId())) {
            throw new IllegalStateException("Ya existe una postulación de ese postulante a ese puesto");
        }

        Postulacion p = new Postulacion(postulante, puesto);
        return repo.save(p);
    }

    public List<Postulacion> listarTodas() {
        return repo.findAll();
    }

    public List<Postulacion> filtrarPorEstado(EstadoPostulacion estado) {
        return repo.findByEstado(estado);
    }

    public List<Postulacion> filtrarPorPuesto(String nombrePuesto) {
        return repo.findByPuestoNombre(nombrePuesto);
    }

    public List<Postulacion> filtrarPorPuestoYEstado(String nombrePuesto, EstadoPostulacion estado) {
        return repo.findByPuestoNombreAndEstado(nombrePuesto, estado);
    }

    public void pasarARevision(Postulacion p) {
        p.pasarARevision();
        repo.save(p);
    }

    public void aprobar(Postulacion p) {
        p.aprobar();
        repo.save(p);
    }

    public void rechazar(Postulacion p) {
        p.rechazar();
        repo.save(p);
    }

    public List<Postulacion> filtrarQueCumplenRequisitos(String nombrePuesto) {
        return repo.findByPuestoNombre(nombrePuesto).stream()
                .filter(this::cumpleRequisitos)
                .toList();
    }

    private boolean cumpleRequisitos(Postulacion post) {
        Requirements req = post.getPuesto().getRequirements();
        CVPerfil perfil = parser.parse(post.getPostulante().getCv());

        boolean expOk = perfil.getExperienceYears() >= req.getMinExperienceYears();
        boolean techOk = perfil.getTechnologies().containsAll(req.getTechnologies());
        boolean inglesOk = perfil.getNivelIngles().ordinal() >= req.getNivelIngles().ordinal();
        boolean tituloOk = !req.requiereTituloUniversitario() || perfil.hasTituloUniversitario();

        return expOk && techOk && inglesOk && techOk && tituloOk;
    }
}