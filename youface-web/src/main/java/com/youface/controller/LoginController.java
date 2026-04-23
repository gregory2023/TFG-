package com.youface.controller;

import com.youface.model.Alumno;
import com.youface.repository.AlumnoRepository;
import jakarta.servlet.http.HttpSession;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

@Controller
public class LoginController {

    @Autowired
    private AlumnoRepository alumnoRepository;

    @GetMapping("/login")
    public String loginPage() {
        return "login";
    }

    @PostMapping("/login")
    public String login(@RequestParam String email,
                        @RequestParam String password,
                        HttpSession session,
                        Model model) {
        Alumno alumno = alumnoRepository.findByEmail(email);
        if (alumno == null || !alumno.getPassword().equals(password)) {
            model.addAttribute("error", "Email o contrasena incorrectos.");
            return "login";
        }
        session.setAttribute("alumno", alumno);
        return "redirect:/panel";
    }
}