package com.youface.controller;

import com.youface.model.Alumno;
import com.youface.repository.AlumnoRepository;
import jakarta.servlet.http.HttpSession;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

@Controller
public class PanelController {

    @Autowired
    private AlumnoRepository alumnoRepository;

    @GetMapping("/panel")
    public String panel(HttpSession session, Model model) {
        Alumno alumno = (Alumno) session.getAttribute("alumno");
        if (alumno == null) return "redirect:/login";
        alumno = alumnoRepository.findById(alumno.getId()).orElse(alumno);
        model.addAttribute("alumno", alumno);
        return "panel";
    }

    @GetMapping("/logout")
    public String logout(HttpSession session) {
        session.invalidate();
        return "redirect:/login";
    }
}