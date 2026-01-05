package org.example.repo;

import org.example.model.Identifiable;

import java.util.List;
import java.util.Optional;

public interface Repository<T extends Identifiable> {
    T save(T entity);

    Optional<T> findById(long id);

    List<T> findAll();

    boolean existsById(long id);

    void deleteById(long id);
}