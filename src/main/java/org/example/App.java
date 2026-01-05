package org.example;

import org.example.model.*;
import org.example.repo.InMemoryPostulacionRepository;
import org.example.repo.PostulacionRepository;
import org.example.service.CVParser;
import org.example.service.PostulacionService;
import org.example.service.RegexCVParser;

import java.util.List;
import java.util.Set;

public class App {

    public static void main(String[] args) {

        // 1) Parser + Service
        CVParser parser = new RegexCVParser();
        PostulacionRepository repo = new InMemoryPostulacionRepository();
        PostulacionService service = new PostulacionService(repo, parser);

        // 2) Puestos y requisitos
        Requirements reqBackend = new Requirements(
                2,                              // minExperienceYears
                Set.of("JAVA", "SQL", "DOCKER"), // technologies esperadas (según tu normalización)
                NivelIngles.INTERMEDIO,
                true
        );

        Puesto backendJunior = new Puesto("Backend Java", reqBackend);

        // 3) Postulantes con CV (rawText simula texto extraído del archivo)
        CV cvNico = new CV("nico_cv.pdf",
                "Tengo 3 años de experiencia. Java, SQL, Docker, Git. Ingles B2. Estudiante de Ingenieria."
        );

        CV cvAna = new CV("ana_cv.pdf",
                "1 año de experiencia. Python, SQL. Ingles basico. Curso terciario."
        );

        CV cvJuan = new CV("juan_cv.pdf",
                "4 años de experiencia en desarrollo. Java, SQL, Docker, AWS. Ingles C1. Licenciatura."
        );

        Postulante nico = new Postulante("Nicolas", "Perez", cvNico);
        Postulante ana = new Postulante("Ana", "Gomez", cvAna);
        Postulante juan = new Postulante("Juan", "Lopez", cvJuan);

        // 4) Crear postulaciones
        service.crear(nico, backendJunior);
        service.crear(ana, backendJunior);
        service.crear(juan, backendJunior);

        // 5) Mostrar todas
        System.out.println("=== Todas las postulaciones ===");
        service.listarTodas().forEach(App::printPostulacion);

        // 6) Filtrar por match con requisitos del puesto
        System.out.println("\n=== Cumplen requisitos (Backend Java) ===");
        List<Postulacion> cumplen = service.filtrarQueCumplenRequisitos("Backend Java");
        cumplen.forEach(App::printPostulacion);

        // 7) Cambiar estado (ej: pasar a revisión las que cumplen)
        cumplen.forEach(service::pasarARevision);

        System.out.println("\n=== En revisión ===");
        service.filtrarPorEstado(EstadoPostulacion.EN_REVISION).forEach(App::printPostulacion);

        // 8) Aprobar el primero (ejemplo)
        if (!cumplen.isEmpty()) {
            service.aprobar(cumplen.get(0));
        }

        System.out.println("\n=== Aprobadas ===");
        service.filtrarPorEstado(EstadoPostulacion.APROBADO).forEach(App::printPostulacion);
    }

    private static void printPostulacion(Postulacion p) {
        System.out.printf(
                "- %s %s -> %s (%s)%n",
                p.getPostulante().getNombre(),
                p.getPostulante().getApellido(),
                p.getPuesto().getNombre(),
                p.getEstado()
        );
    }
}