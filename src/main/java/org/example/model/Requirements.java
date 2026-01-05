package org.example.model;

import java.util.Set;

public class Requirements {

    private final int minExperienceYears;
    private final Set<String> technologies;
    private final NivelIngles nivelIngles;
    private final boolean tituloUniversitario;

    public Requirements(int minExperienceYears,
                        Set<String> technologies,
                        NivelIngles nivelIngles,
                        boolean tituloUniversitario) {

        if (minExperienceYears < 0 || technologies == null || nivelIngles == null) {
            throw new IllegalArgumentException("Requisitos inválidos");
        }

        this.minExperienceYears = minExperienceYears;
        this.technologies = Set.copyOf(technologies); // inmutable
        this.nivelIngles = nivelIngles;
        this.tituloUniversitario = tituloUniversitario;
    }

    public int getMinExperienceYears() {
        return minExperienceYears;
    }

    public Set<String> getTechnologies() {
        return technologies;
    }

    public NivelIngles getNivelIngles() {
        return nivelIngles;
    }

    public boolean requiereTituloUniversitario() {
        return tituloUniversitario;
    }
}