package org.example.model;

import java.util.concurrent.atomic.AtomicLong;

public class Postulante {
    private static final AtomicLong SEQ = new AtomicLong(1);

    private final long id;
    private final String nombre;
    private final String apellido;
    private final CV cv;

    public Postulante(String nombre, String apellido, CV cv) {
        this.id = SEQ.getAndIncrement();
        this.nombre = nombre;
        this.apellido = apellido;
        this.cv = cv;
    }

    public long getId() { return id; }
    public String getNombre() { return nombre; }
    public String getApellido() { return apellido; }
    public CV getCv() { return cv; }
}