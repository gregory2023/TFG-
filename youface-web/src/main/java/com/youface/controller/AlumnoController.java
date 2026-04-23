package com.youface.controller;

import com.youface.model.Alumno;
import com.youface.service.AlumnoService;
import com.youface.repository.AlumnoRepository;
import jakarta.servlet.http.HttpSession;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

@Controller
public class AlumnoController {

    @Autowired
    private AlumnoService alumnoService;

    @Autowired
    private AlumnoRepository alumnoRepository;

    @GetMapping("/registro-biometrico")
    public String registroPage(HttpSession session, Model model) {
        Alumno alumno = (Alumno) session.getAttribute("alumno");
        if (alumno == null) return "redirect:/login";
        model.addAttribute("alumno", alumno);
        return "registro";
    }

    @PostMapping("/registrar")
    public String registrar(
            @ModelAttribute Alumno alumnoForm,
            @RequestParam("foto1") MultipartFile foto1,
            @RequestParam("foto2") MultipartFile foto2,
            @RequestParam("foto3") MultipartFile foto3,
            @RequestParam("foto4") MultipartFile foto4,
            @RequestParam("foto5") MultipartFile foto5,
            HttpSession session,
            Model model) {

        try {
            Alumno alumno = (Alumno) session.getAttribute("alumno");
            if (alumno == null) return "redirect:/login";

            alumno = alumnoRepository.findById(alumno.getId()).orElse(alumno);
            alumnoService.registrarAlumno(alumno, foto1, foto2, foto3, foto4, foto5);
            session.setAttribute("alumno", alumno);
            model.addAttribute("exito", "Datos biometricos registrados correctamente.");
            model.addAttribute("alumno", alumno);
        } catch (Exception e) {
            model.addAttribute("error", "Error al registrar: " + e.getMessage());
        }
        return "registro";
    }

    @GetMapping("/alumnos")
    public String listarAlumnos(Model model) {
        model.addAttribute("alumnos", alumnoService.listarAlumnos());
        return "alumnos";
    }
}