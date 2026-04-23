package com.youface.service;

import com.youface.model.Alumno;
import com.youface.repository.AlumnoRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials;
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider;
import software.amazon.awssdk.core.sync.RequestBody;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.PutObjectRequest;

import java.io.IOException;
import java.util.List;
import java.util.UUID;

@Service
public class AlumnoService {

    @Autowired
    private AlumnoRepository alumnoRepository;

    @Value("${aws.access-key}")
    private String accessKey;

    @Value("${aws.secret-key}")
    private String secretKey;

    @Value("${aws.region}")
    private String region;

    @Value("${aws.s3.bucket}")
    private String bucket;

    private S3Client getS3Client() {
        return S3Client.builder()
                .region(Region.of(region))
                .credentialsProvider(StaticCredentialsProvider.create(
                        AwsBasicCredentials.create(accessKey, secretKey)))
                .build();
    }

    private String subirFotoS3(MultipartFile foto, String nombreAlumno) throws IOException {
        S3Client s3 = getS3Client();
        String nombreArchivo = "alumnos/" + nombreAlumno + "/" + UUID.randomUUID() + ".jpg";

        s3.putObject(
                PutObjectRequest.builder()
                        .bucket(bucket)
                        .key(nombreArchivo)
                        .contentType("image/jpeg")
                        .build(),
                RequestBody.fromBytes(foto.getBytes())
        );

        return "https://" + bucket + ".s3." + region + ".amazonaws.com/" + nombreArchivo;
    }

    public void registrarAlumno(Alumno alumno, MultipartFile foto1,
                                MultipartFile foto2, MultipartFile foto3,
                                MultipartFile foto4, MultipartFile foto5) throws IOException {
        String nombreCarpeta = alumno.getNombre().replace(" ", "_");

        if (!foto1.isEmpty()) alumno.setFoto1Url(subirFotoS3(foto1, nombreCarpeta));
        if (!foto2.isEmpty()) alumno.setFoto2Url(subirFotoS3(foto2, nombreCarpeta));
        if (!foto3.isEmpty()) alumno.setFoto3Url(subirFotoS3(foto3, nombreCarpeta));
        if (!foto4.isEmpty()) alumno.setFoto4Url(subirFotoS3(foto4, nombreCarpeta));
        if (!foto5.isEmpty()) alumno.setFoto5Url(subirFotoS3(foto5, nombreCarpeta));

        alumnoRepository.save(alumno);
    }

    public List<Alumno> listarAlumnos() {
        return alumnoRepository.findAll();
    }

    public boolean existeAlumno(String dni) {
        return alumnoRepository.existsByDni(dni);
    }
}