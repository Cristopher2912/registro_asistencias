import cv2
import numpy as np
import base64
import os
from io import BytesIO
from PIL import Image
from db import obtener_estudiantes

# Cargar detector Haar Cascade
detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
if detector.empty():
    print("Error cargando el detector Haar Cascade")

def decodificar_imagen(base64_str):
    """Convierte imagen base64 a OpenCV BGR"""
    try:
        img_data = base64.b64decode(base64_str.split(',')[1])
        print(f"Tamaño bytes imagen decodificada: {len(img_data)}")
        img_pil = Image.open(BytesIO(img_data)).convert('RGB')
        img_np = np.array(img_pil)
        return cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    except Exception as e:
        print(f"Error decodificando imagen: {e}")
        return None

def extraer_rostro(img_bgr):
    """Detecta rostro y devuelve recorte"""
    gris = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    rostros = detector.detectMultiScale(gris, 1.3, 5)
    if len(rostros) == 0:
        print("No se detectaron rostros")
        return None
    for (x, y, w, h) in rostros:
        print(f"Rostro detectado en coordenadas: x={x}, y={y}, w={w}, h={h}")
        return gris[y:y+h, x:x+w]
    return None

def reconocer_estudiante(base64_img):
    imagen_bgr = decodificar_imagen(base64_img)
    if imagen_bgr is None:
        print("Imagen no válida para reconocimiento")
        return None

    rostro_desconocido = extraer_rostro(imagen_bgr)
    if rostro_desconocido is None:
        print("No se detectó rostro en la imagen capturada")
        return None

    estudiantes = obtener_estudiantes()
    for est_id, nombre, ruta, *rest in estudiantes:  # En caso que haya más columnas
        print(f"Probando contra estudiante: {nombre}")
        ruta_img = os.path.join("static/fotos", ruta)
        if not os.path.exists(ruta_img):
            print(f"Foto no encontrada para estudiante {nombre} en {ruta_img}")
            continue
        img_registrada = cv2.imread(ruta_img)
        if img_registrada is None:
            print(f"No se pudo leer la imagen para estudiante {nombre}")
            continue
        rostro_registrado = extraer_rostro(img_registrada)
        if rostro_registrado is None:
            print(f"No se detectó rostro en la foto registrada de {nombre}")
            continue

        try:
            rostro_registrado = cv2.resize(rostro_registrado, (100, 100))
            rostro_desconocido = cv2.resize(rostro_desconocido, (100, 100))
        except Exception as e:
            print(f"Error redimensionando rostros: {e}")
            continue

        diferencia = cv2.absdiff(rostro_desconocido, rostro_registrado)
        puntuacion = np.mean(diferencia)
        print(f"Comparación con {nombre}: puntuación de diferencia = {puntuacion}")

        if puntuacion < 40:  # Ajusta umbral según necesites
            print(f"Rostro reconocido: {nombre} con puntuación {puntuacion}")
            return est_id, nombre

    print("No se encontró coincidencia para el rostro")
    return None
