package org.example.model;

import java.util.concurrent.atomic.AtomicLong;

public class Puesto {
    private static final AtomicLong SEQ = new AtomicLong(1);

    private final long id;
    private final String nombre;
    private final Requirements requirements;

    public Puesto(String nombre, Requirements requirements) {
        this.id = SEQ.getAndIncrement();
        this.nombre = nombre;
        this.requirements = requirements;
    }

    public long getId() { return id; }
    public String getNombre() { return nombre; }
    public Requirements getRequirements() { return requirements; }
}