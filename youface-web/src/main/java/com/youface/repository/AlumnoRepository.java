package com.youface.repository;

import com.youface.model.Alumno;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface AlumnoRepository extends JpaRepository<Alumno, Long> {
    Alumno findByDni(String dni);
    Alumno findByEmail(String email);
    boolean existsByDni(String dni);
    boolean existsByEmail(String email);
}