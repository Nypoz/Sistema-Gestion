package org.example.service;

import org.example.model.CV;
import org.example.model.CVPerfil;

public interface CVParser {
    CVPerfil parse(CV cv);
}