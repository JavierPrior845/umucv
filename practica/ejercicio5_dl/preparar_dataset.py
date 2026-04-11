#!/usr/bin/env python

import cv2 as cv
import numpy as np
import os
import mediapipe as mp
from umucv.stream import autoStream
from umucv.util import putText

# --- CONFIGURACIÓN ---
# Carpeta de salida (asegurado que existen por el script principal)
DATA_DIR = "train"
IMG_DIR = os.path.join(DATA_DIR, "images")
LBL_DIR = os.path.join(DATA_DIR, "labels")
os.makedirs(IMG_DIR, exist_ok=True)
os.makedirs(LBL_DIR, exist_ok=True)

# MediaPipe Face Mesh para auto-etiquetado
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    min_detection_confidence=0.5)

# Índices de la boca en FaceMesh (algunos puntos clave del contorno)
MOUTH_INDICES = [0, 13, 14, 17, 37, 39, 40, 61, 78, 80, 81, 82, 84, 87, 88, 91, 95, 146, 178, 181, 191, 267, 269, 270, 291, 308, 310, 311, 312, 314, 317, 318, 321, 324, 325, 375, 402, 405, 415]

N = 0
print("\nPREPARADOR DE DATASET: DETECTOR DE BOCA")
print("1. En cada segundo se captura una imagen automáticamente.")
print("2. Mueve la cabeza, abre y cierra la boca para tener variedad.")
print("3. Pulsa 'ESC' para terminar.")

for k, (key, frame) in enumerate(autoStream()):
    h, w = frame.shape[:2]
    display_frame = frame.copy()
    
    # Procesar con MediaPipe
    rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)
    
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # Extraer coordenadas de los puntos de la boca
            coords = []
            for idx in MOUTH_INDICES:
                lm = face_landmarks.landmark[idx]
                coords.append((int(lm.x * w), int(lm.y * h)))
            
            coords = np.array(coords)
            # Calcular Bounding Box (YOLO format)
            x0, y0 = np.min(coords, axis=0)
            x1, y1 = np.max(coords, axis=0)
            
            # Dibujar para feedback
            cv.rectangle(display_frame, (x0, y0), (x1, y1), (0, 255, 0), 1)
            
            # Guardar cada 20 frames (aprox 1 vez por segundo)
            if k % 20 == 0:
                N += 1
                img_path = os.path.join(IMG_DIR, f"{N:04d}.jpg")
                lbl_path = os.path.join(LBL_DIR, f"{N:04d}.txt")
                
                # Imagen
                cv.imwrite(img_path, frame)
                
                # Etiqueta YOLO: <class_id> <x_center> <y_center> <width> <height> (normalizados 0-1)
                xc = (x0 + x1) / 2 / w
                yc = (y0 + y1) / 2 / h
                bw = (x1 - x0) / w
                bh = (y1 - y0) / h
                
                with open(lbl_path, "w") as f:
                    f.write(f"0 {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}\n")
                
                print(f"[{N}] Imagen guardada en {img_path}")

    putText(display_frame, f"Capturadas: {N}", (10, 30))
    cv.imshow("Captura de Dataset", display_frame)
    if key == 27: break

print(f"\nProceso terminado. Se han capturado {N} imágenes.")
print("Ahora debes copiar al menos un par de ellas a la carpeta 'val/' para la validación.")
