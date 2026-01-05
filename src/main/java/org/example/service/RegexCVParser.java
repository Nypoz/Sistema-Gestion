package org.example.service;

import org.example.model.CV;
import org.example.model.CVPerfil;
import org.example.model.NivelIngles;

import java.text.Normalizer;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class RegexCVParser implements CVParser {

    // Diccionario simple (lo podés ampliar)
    private static final Set<String> TECHNOLOGIES = Set.of(
            "java", "python", "javascript", "typescript", "sql", "mysql", "postgresql",
            "spring", "hibernate", "docker", "kubernetes", "aws", "azure", "gcp",
            "react", "node", "git", "linux"
    );

    // Captura cosas tipo: "3 años de experiencia", "5 anos experiencia", "2+ años"
    private static final Pattern YEARS_PATTERN = Pattern.compile(
            "(\\d{1,2})\\s*\\+?\\s*(?:anos|años)\\s*(?:de\\s*)?(?:experiencia|exp\\b)?",
            Pattern.CASE_INSENSITIVE
    );

    @Override
    public CVPerfil parse(CV cv) {
        String text = normalize(cv.getRawText());

        int years = extractExperienceYears(text);
        Set<String> techs = extractTechnologies(text);
        NivelIngles english = extractEnglishLevel(text);
        boolean titulo = extractUniversityDegree(text);

        return new CVPerfil(years, techs, english, titulo);
    }

    private int extractExperienceYears(String text) {
        int best = 0;
        Matcher m = YEARS_PATTERN.matcher(text);
        while (m.find()) {
            int val = safeParseInt(m.group(1));
            if (val > best) best = val;
        }
        return best;
    }

    private Set<String> extractTechnologies(String text) {
        Set<String> found = new HashSet<>();
        for (String tech : TECHNOLOGIES) {
            // palabra completa cuando aplica; para cosas como "c" no lo uses así (acá no está)
            Pattern p = Pattern.compile("\\b" + Pattern.quote(tech) + "\\b", Pattern.CASE_INSENSITIVE);
            if (p.matcher(text).find()) {
                found.add(tech.toUpperCase()); // o mantener original; gusto personal
            }
        }
        return found;
    }

    private NivelIngles extractEnglishLevel(String text) {
        // Orden importa: detectamos primero niveles más altos
        if (containsAny(text, "native", "nativo", "bilingual", "bilingue", "c2")) return NivelIngles.FLUIDO;
        if (containsAny(text, "advanced", "avanzado", "c1")) return NivelIngles.AVANZADO;
        if (containsAny(text, "intermediate", "intermedio", "b1", "b2")) return NivelIngles.INTERMEDIO;
        if (containsAny(text, "basic", "basico", "a1", "a2")) return NivelIngles.BASICO;

        // Si no dice nada, por defecto: básico (o podrías usar null/UNKNOWN si creás ese enum)
        return NivelIngles.BASICO;
    }

    private boolean extractUniversityDegree(String text) {
        return containsAny(text,
                "licenciatura", "ingenieria", "ingeniería", "universidad", "titulo universitario",
                "bachelor", "master", "msc", "phd", "doctorado"
        );
    }

    private boolean containsAny(String text, String... keywords) {
        for (String k : keywords) {
            if (text.contains(normalize(k))) return true;
        }
        return false;
    }

    private int safeParseInt(String s) {
        try { return Integer.parseInt(s); }
        catch (Exception e) { return 0; }
    }

    private String normalize(String s) {
        String lower = (s == null) ? "" : s.toLowerCase(Locale.ROOT);
        String noAccents = Normalizer.normalize(lower, Normalizer.Form.NFD)
                .replaceAll("\\p{M}", "");
        return noAccents;
    }
}