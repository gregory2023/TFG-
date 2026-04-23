package com.youface.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "alumnos")
public class Alumno {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String nombre;

    @Column(nullable = false, unique = true)
    private String dni;

    @Column(nullable = false)
    private String email;

    @Column(nullable = false)
    private String password;

    @Column(name = "foto1_url")
    private String foto1Url;

    @Column(name = "foto2_url")
    private String foto2Url;

    @Column(name = "foto3_url")
    private String foto3Url;

    @Column(name = "foto4_url")
    private String foto4Url;

    @Column(name = "foto5_url")
    private String foto5Url;

    @Column(name = "fecha_registro")
    private LocalDateTime fechaRegistro;

    @PrePersist
    public void prePersist() {
        fechaRegistro = LocalDateTime.now();
    }

    // Getters y Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getNombre() { return nombre; }
    public void setNombre(String nombre) { this.nombre = nombre; }

    public String getDni() { return dni; }
    public void setDni(String dni) { this.dni = dni; }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    public String getFoto1Url() { return foto1Url; }
    public void setFoto1Url(String foto1Url) { this.foto1Url = foto1Url; }

    public String getFoto2Url() { return foto2Url; }
    public void setFoto2Url(String foto2Url) { this.foto2Url = foto2Url; }

    public String getFoto3Url() { return foto3Url; }
    public void setFoto3Url(String foto3Url) { this.foto3Url = foto3Url; }

    public String getFoto4Url() { return foto4Url; }
    public void setFoto4Url(String foto4Url) { this.foto4Url = foto4Url; }

    public String getFoto5Url() { return foto5Url; }
    public void setFoto5Url(String foto5Url) { this.foto5Url = foto5Url; }

    public String getPassword() { return password; }
    public void setPassword(String password) { this.password = password; }


    public LocalDateTime getFechaRegistro() { return fechaRegistro; }
    public void setFechaRegistro(LocalDateTime fechaRegistro) { this.fechaRegistro = fechaRegistro;}
    }