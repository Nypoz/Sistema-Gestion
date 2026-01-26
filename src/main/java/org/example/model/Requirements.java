package org.example.model;

import java.util.Set;
import java.util.Objects;
import java.util.stream.Collectors;

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
        this.technologies = normalizeTechnologies(technologies);
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

    private Set<String> normalizeTechnologies(Set<String> techs) {
        return techs.stream()
                .filter(Objects::nonNull)
                .map(String::trim)
                .filter(s -> !s.isEmpty())
                .map(String::toUpperCase)
                .collect(Collectors.toUnmodifiableSet());
    }
}