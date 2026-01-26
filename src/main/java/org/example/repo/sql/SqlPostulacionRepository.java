package org.example.repo.sql;

import org.example.model.*;
import org.example.repo.PostulacionRepository;

import java.sql.*;
import java.util.ArrayList;
import java.util.List;

public class SqlPostulacionRepository implements PostulacionRepository {

    @Override
    public Postulacion save(Postulacion p) {
        try (Connection conn = Database.getConnection()) {

            PreparedStatement stmt = conn.prepareStatement("""
                INSERT OR REPLACE INTO postulacion (id, postulante_id, puesto_id, estado)
                VALUES (?, ?, ?, ?)
            """);

            stmt.setLong(1, p.getId());
            stmt.setLong(2, p.getPostulante().getId());
            stmt.setLong(3, p.getPuesto().getId());
            stmt.setString(4, p.getEstado().name());

            stmt.executeUpdate();
            return p;

        } catch (SQLException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public List<Postulacion> findAll() {
        return new ArrayList<>(); // lo implementamos después
    }
}