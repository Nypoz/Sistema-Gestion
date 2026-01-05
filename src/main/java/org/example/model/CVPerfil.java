package org.example.model;

import java.util.Set;

public class CVPerfil {
    private final int experienceYears;
    private final Set<String> technologies;
    private final NivelIngles nivelIngles;
    private final boolean tituloUniversitario;

    public CVPerfil(int experienceYears, Set<String> technologies, NivelIngles nivelIngles, boolean tituloUniversitario) {
        this.experienceYears = experienceYears;
        this.technologies = Set.copyOf(technologies);
        this.nivelIngles = nivelIngles;
        this.tituloUniversitario = tituloUniversitario;
    }

    public int getExperienceYears() { return experienceYears; }
    public Set<String> getTechnologies() { return technologies; }
    public NivelIngles getNivelIngles() { return nivelIngles; }
    public boolean hasTituloUniversitario() { return tituloUniversitario; }
}