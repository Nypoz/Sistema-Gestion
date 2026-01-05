package org.example.repo;

import org.example.model.Identifiable;

import java.util.*;

public class InMemoryRepository<T extends Identifiable> implements Repository<T> {

    private final Map<Long, T> storage = new HashMap<>();

    @Override
    public T save(T entity) {
        storage.put(entity.getId(), entity);
        return entity;
    }

    @Override
    public Optional<T> findById(long id) {
        return Optional.ofNullable(storage.get(id));
    }

    @Override
    public List<T> findAll() {
        return List.copyOf(storage.values());
    }

    @Override
    public boolean existsById(long id) {
        return storage.containsKey(id);
    }

    @Override
    public void deleteById(long id) {
        storage.remove(id);
    }
}