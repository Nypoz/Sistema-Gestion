package org.example.model;

import java.util.concurrent.atomic.AtomicLong;

public class Postulacion implements Identifiable {
    private static final AtomicLong SEQ = new AtomicLong(1);

    private final long id;
    private final Postulante postulante;
    private final Puesto puesto;
    private EstadoPostulacion estado;

    public Postulacion(Postulante postulante, Puesto puesto) {
        this.id = SEQ.getAndIncrement();
        this.postulante = postulante;
        this.puesto = puesto;
        this.estado = EstadoPostulacion.PENDIENTE;
    }

    public long getId() { return id; }
    public Postulante getPostulante() { return postulante; }
    public Puesto getPuesto() { return puesto; }
    public EstadoPostulacion getEstado() { return estado; }

    public void pasarARevision() { estado = EstadoPostulacion.EN_REVISION; }
    public void aprobar() { estado = EstadoPostulacion.APROBADO; }
    public void rechazar() { estado = EstadoPostulacion.RECHAZADO; }
}