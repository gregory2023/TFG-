import cv2
import time
import requests
import os
import threading
import boto3
import shutil
import pandas as pd
from deepface import DeepFace
from dotenv import load_dotenv
from ultralytics import YOLO
from urllib.parse import urlparse

load_dotenv()

# ── Configuración ──────────────────────────────────────────────
CAMARA = 0
INTERVALO_RECONOCIMIENTO = 5
API_URL = os.getenv("API_URL", "http://13.61.34.115:8000")
INTERVALO_ALERTA = 5
CARPETA_USUARIOS = "local_client/usuarios_registrados"

# ── S3 ─────────────────────────────────────────────────────────
s3 = boto3.client(
    "s3",
    region_name=os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)
S3_BUCKET = os.getenv("S3_BUCKET", "tfg-vision-capturas")

# ── YOLO ───────────────────────────────────────────────────────
model = YOLO("yolov8n.pt")
OBJETOS_SOSPECHOSOS = {67: "movil", 63: "laptop"}

# ── Descargar fotos desde S3 ───────────────────────────────────
def extraer_key_s3(url):
    return urlparse(url).path.lstrip("/")

def descargar_fotos_alumnos():
    print("[INFO] Descargando fotos desde S3...")
    try:
        if os.path.exists(CARPETA_USUARIOS):
            shutil.rmtree(CARPETA_USUARIOS)
        os.makedirs(CARPETA_USUARIOS)

        response = requests.get(f"{API_URL}/alumnos", timeout=10)
        alumnos = response.json()

        for alumno in alumnos:
            nombre = alumno["nombre"].replace(" ", "_")
            carpeta = os.path.join(CARPETA_USUARIOS, nombre)
            os.makedirs(carpeta, exist_ok=True)

            fotos = [alumno.get(f"foto{i}_url") for i in range(1, 6)]
            fotos = [f for f in fotos if f]

            for i, url in enumerate(fotos):
                try:
                    key = extraer_key_s3(url)
                    foto_path = os.path.join(carpeta, f"foto_{i+1}.jpg")
                    s3.download_file(S3_BUCKET, key, foto_path)
                    print(f"[INFO] Descargada: {foto_path}")
                except Exception as e:
                    print(f"[WARN] Error foto {i+1} de {nombre}: {e}")

        print(f"[INFO] {len(alumnos)} alumno(s) cargados.")
        return True
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

# ── Estado compartido ──────────────────────────────────────────
usuario_actual        = None
reconociendo          = False
ultima_alerta_enviada = 0

def subir_captura_s3(frame, nombre_archivo):
    try:
        _, buffer = cv2.imencode(".jpg", frame)
        s3.put_object(Bucket=S3_BUCKET, Key=f"infracciones/{nombre_archivo}",
                      Body=buffer.tobytes(), ContentType="image/jpeg")
        print(f"[S3] Captura subida: {nombre_archivo}")
    except Exception as e:
        print(f"[S3] Error: {e}")

def enviar_alerta(user_id, alert_type):
    try:
        r = requests.post(f"{API_URL}/alerta",
                          json={"user_id": user_id, "alert_type": alert_type}, timeout=3)
        if r.status_code == 200:
            print(f"[API] OK: {alert_type} — {user_id}")
    except Exception as e:
        print(f"[API] Error: {e}")

def reconocer_en_hilo(frame):
    """Usa DeepFace.find() para buscar en toda la base de datos de una vez."""
    global usuario_actual, reconociendo
    try:
        resultado = DeepFace.find(
            img_path=frame,
            db_path=CARPETA_USUARIOS,
            model_name="Facenet",
            enforce_detection=False,
            silent=True
        )
        if resultado and len(resultado) > 0 and not resultado[0].empty:
            ruta = resultado[0].iloc[0]["identity"]
            nombre = ruta.split(os.sep)[-2]
            usuario_actual = nombre
        else:
            usuario_actual = None
    except Exception as e:
        usuario_actual = None
    reconociendo = False
    print(f"[DeepFace] Resultado: {usuario_actual if usuario_actual else 'desconocido'}")

def detectar_objetos(frame):
    resultados = model(frame, verbose=False, conf=0.45)
    detectados = []
    for r in resultados:
        for box in r.boxes:
            clase_id = int(box.cls[0])
            if clase_id in OBJETOS_SOSPECHOSOS:
                nombre = OBJETOS_SOSPECHOSOS[clase_id]
                conf = float(box.conf[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(frame, f"{nombre} {conf:.0%}",
                            (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                detectados.append(nombre)
    return detectados, frame

def dibujar_hud(frame, usuario, objetos, reconociendo):
    h, w = frame.shape[:2]
    cv2.rectangle(frame, (0, 0), (w, 80), (15, 15, 15), -1)
    if reconociendo:
        cv2.putText(frame, "Identificando alumno...", (10, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (200, 200, 0), 2)
    elif usuario:
        cv2.putText(frame, f"Alumno: {usuario}", (10, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 220, 100), 2)
        cv2.putText(frame, "Acceso al examen: REGISTRADO", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 220, 100), 2)
    else:
        cv2.putText(frame, "Alumno: desconocido", (10, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (100, 100, 100), 2)
        cv2.putText(frame, "Acceso: NO AUTORIZADO", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 220), 2)
    if objetos:
        cv2.rectangle(frame, (0, 0), (w, h), (0, 0, 200), 3)
        cv2.putText(frame, f"INFRACCION: {', '.join(objetos).upper()} DETECTADO",
                    (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 80, 255), 2)
    return frame

def main():
    global reconociendo, ultima_alerta_enviada

    descargado = descargar_fotos_alumnos()
    if not descargado:
        print("[WARN] Usando fotos locales si existen.")

    if not os.path.exists(CARPETA_USUARIOS) or not os.listdir(CARPETA_USUARIOS):
        print("[ERROR] No hay alumnos registrados.")
        return

    # Preconstruir la base de datos vectorial de DeepFace
    print("[INFO] Construyendo base de datos facial... (solo la primera vez)")
    try:
        DeepFace.find(img_path=CARPETA_USUARIOS + "/placeholder",
                      db_path=CARPETA_USUARIOS, model_name="Facenet",
                      enforce_detection=False, silent=True)
    except:
        pass

    cap = cv2.VideoCapture(CAMARA)
    if not cap.isOpened():
        print("[ERROR] No se puede abrir la camara.")
        return

    print(f"[INFO] Modo examen activo. Pulsa Q para salir.")
    ultimo_analisis = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        ahora = time.time()

        if ahora - ultimo_analisis >= INTERVALO_RECONOCIMIENTO and not reconociendo:
            ultimo_analisis = ahora
            reconociendo = True
            frame_copia = frame.copy()
            t = threading.Thread(target=reconocer_en_hilo, args=(frame_copia,))
            t.daemon = True
            t.start()

            if usuario_actual and ahora - ultima_alerta_enviada >= INTERVALO_ALERTA:
                enviar_alerta(usuario_actual, "acceso_examen")
                ultima_alerta_enviada = ahora

        objetos, frame = detectar_objetos(frame)

        if objetos and ahora - ultima_alerta_enviada >= INTERVALO_ALERTA:
            uid = usuario_actual if usuario_actual else "desconocido"
            enviar_alerta(uid, f"infraccion_{objetos[0]}")
            ultima_alerta_enviada = ahora
            nombre_archivo = f"{uid}_{objetos[0]}_{time.strftime('%Y%m%d_%H%M%S')}.jpg"
            t_s3 = threading.Thread(target=subir_captura_s3, args=(frame.copy(), nombre_archivo))
            t_s3.daemon = True
            t_s3.start()

        frame = dibujar_hud(frame, usuario_actual, objetos, reconociendo)
        cv2.imshow("TFG Vision System - Modo Examen", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
