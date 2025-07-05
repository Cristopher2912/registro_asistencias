import cv2
import numpy as np
import base64
import os
from io import BytesIO
from PIL import Image
from db import obtener_estudiantes
import pickle

# Inicializar detector y reconocedor LBPH
detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
recognizer = cv2.face.LBPHFaceRecognizer_create()

label_to_id_map = {}
modelo_path = "modelo_reconocimiento_facial.yml"
labelmap_path = "label_map.pkl"

def decodificar_imagen(base64_str):
    try:
        img_data = base64.b64decode(base64_str.split(',')[1])
        img_pil = Image.open(BytesIO(img_data)).convert('RGB')
        img_np = np.array(img_pil)
        return cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    except Exception as e:
        print(f"Error al decodificar imagen base64: {e}")
        return None

def extraer_rostro(img_bgr, required_size=(100, 100)):
    gris = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    rostros = detector.detectMultiScale(gris, 1.3, 5, minSize=(30, 30))
    if len(rostros) == 0:
        return None
    (x, y, w, h) = max(rostros, key=lambda r: r[2] * r[3])
    rostro = gris[y:y+h, x:x+w]
    try:
        rostro = cv2.resize(rostro, required_size)
        rostro = cv2.equalizeHist(rostro)
        return rostro
    except:
        return None

def generar_variaciones(rostro):
    variaciones = [rostro]
    rows, cols = rostro.shape

    for angle in [-10, -5, 5, 10]:
        M = cv2.getRotationMatrix2D((cols / 2, rows / 2), angle, 1)
        rotada = cv2.warpAffine(rostro, M, (cols, rows))
        variaciones.append(rotada)

    for beta in [-30, 30]:
        brillo = cv2.convertScaleAbs(rostro, alpha=1, beta=beta)
        variaciones.append(brillo)

    return variaciones

def entrenar_reconocedor():
    global label_to_id_map
    print("Entrenando modelo facial...")
    faces = []
    labels = []
    estudiante_ids = {}
    current_label = 0

    estudiantes = obtener_estudiantes()
    for est_id, nombre, ruta, *rest in estudiantes:
        ruta_img = os.path.join("static/fotos", ruta)
        if not os.path.exists(ruta_img):
            print(f"Imagen no encontrada: {ruta_img}")
            continue
        img = cv2.imread(ruta_img)
        if img is None:
            print(f"No se pudo cargar la imagen: {ruta_img}")
            continue
        rostro = extraer_rostro(img)
        if rostro is None:
            print(f"No se detectó rostro en imagen de {nombre}")
            continue
        if est_id not in estudiante_ids:
            estudiante_ids[est_id] = current_label
            current_label += 1

        variaciones = generar_variaciones(rostro)
        faces.extend(variaciones)
        labels.extend([estudiante_ids[est_id]] * len(variaciones))
        print(f"Entrenado con {nombre}, Label {estudiante_ids[est_id]}")

    if not faces:
        print("No se encontraron rostros válidos.")
        return False

    recognizer.train(faces, np.array(labels))
    recognizer.save(modelo_path)
    label_to_id_map = {v: k for k, v in estudiante_ids.items()}
    with open(labelmap_path, "wb") as f:
        pickle.dump(label_to_id_map, f)
    print("Modelo entrenado y guardado.")
    return True

# Cargar modelo si existe
if os.path.exists(modelo_path) and os.path.exists(labelmap_path):
    recognizer.read(modelo_path)
    with open(labelmap_path, "rb") as f:
        label_to_id_map = pickle.load(f)
    print("Modelo facial y mapa de etiquetas cargados.")
else:
    entrenar_reconocedor()

def reconocer_estudiante(base64_img):
    if not label_to_id_map:
        print("Modelo no entrenado. No se puede reconocer.")
        return None

    imagen_bgr = decodificar_imagen(base64_img)
    if imagen_bgr is None:
        return None
    rostro = extraer_rostro(imagen_bgr)
    if rostro is None:
        return None

    try:
        label_predicho, confianza = recognizer.predict(rostro)
        print(f"Predicción: Label {label_predicho}, Confianza {confianza}")
        UMBRAL = 130
        if confianza < UMBRAL:
            est_id = label_to_id_map.get(label_predicho)
            if est_id:
                estudiantes = obtener_estudiantes()
                for eid, nombre, *_ in estudiantes:
                    if eid == est_id:
                        return est_id, nombre
    except Exception as e:
        print(f"Error al reconocer rostro: {e}")
    return None
