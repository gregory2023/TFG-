package com.youface.controller;

import com.youface.model.Alumno;
import com.youface.repository.AlumnoRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

@Controller
public class SignupController {

    @Autowired
    private AlumnoRepository alumnoRepository;

    @GetMapping("/signup")
    public String signupPage() {
        return "signup";
    }

    @PostMapping("/signup")
    public String signup(@RequestParam String nombre,
                         @RequestParam String dni,
                         @RequestParam String email,
                         @RequestParam String password,
                         Model model) {
        if (alumnoRepository.existsByEmail(email)) {
            model.addAttribute("error", "Ya existe una cuenta con ese email.");
            return "signup";
        }
        if (alumnoRepository.existsByDni(dni)) {
            model.addAttribute("error", "Ya existe una cuenta con ese DNI.");
            return "signup";
        }
        Alumno alumno = new Alumno();
        alumno.setNombre(nombre);
        alumno.setDni(dni);
        alumno.setEmail(email);
        alumno.setPassword(password);
        alumnoRepository.save(alumno);
        return "redirect:/login";
    }
}