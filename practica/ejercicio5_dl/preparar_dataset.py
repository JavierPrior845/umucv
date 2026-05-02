#!/usr/bin/env python

import cv2 as cv
import numpy as np
import os
from umucv.stream import autoStream
from umucv.util import ROI, putText

# --- CONFIGURACIÓN ---
DATA_DIR = "train"
IMG_DIR = os.path.join(DATA_DIR, "images")
LBL_DIR = os.path.join(DATA_DIR, "labels")
os.makedirs(IMG_DIR, exist_ok=True)
os.makedirs(LBL_DIR, exist_ok=True)

# Manejador del ratón para dibujar cajas
region = ROI("Etiquetador Manual")

print("\n--- ETIQUETADOR MANUAL DE YOLO ---")
print("1. El vídeo empezará a reproducirse.")
print("2. Pulsa la BARRA ESPACIADORA para pausar el vídeo cuando veas el objeto.")
print("3. Usa el raton para arrastrar y dibujar un cuadrado sobre el objeto.")
print("4. Pulsa 's' para Guardar la imagen y la etiqueta.")
print("5. Pulsa 'q' o ESC para salir.")

generador_stream = autoStream()

try:
    key_stream, frame = next(generador_stream)
except StopIteration:
    print("Vaya, no se ha podido abrir la cámara o vídeo.")
    exit()

paused = False
import glob
existing_files = glob.glob(os.path.join(IMG_DIR, "obj_*.jpg"))
if existing_files:
    indices = [int(os.path.basename(f).split('_')[1].split('.')[0]) for f in existing_files if f.split('_')[1].split('.')[0].isdigit()]
    N = max(indices) if indices else 0
else:
    N = 0

while True:
    display_frame = frame.copy()
    h, w = frame.shape[:2]

    # Dibujar la caja interactiva
    if region.roi:
        [x1, y1, x2, y2] = region.roi
        # Asegurar coordenadas bien ordenadas (arriba-izq, abajo-der)
        x_min, x_max = min(x1, x2), max(x1, x2)
        y_min, y_max = min(y1, y2), max(y1, y2)
        
        cv.rectangle(display_frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)

    # UI Feedback
    estado = "PAUSADO (Dibuja y pulsa 's' para guardar)" if paused else "REPRODUCIENDO (Pulsa ESPACIO para pausar)"
    color_estado = (0, 0, 255) if paused else (0, 255, 0)
    putText(display_frame, estado, (10, 30), color=color_estado, scale=1.5, div=2)
    putText(display_frame, f"Guardadas: {N}   (Objetivo: ~40)", (10, 60))

    cv.imshow("Etiquetador Manual", display_frame)
    
    # Procesar teclado
    key = cv.waitKey(30) & 0xFF
    
    if key == 27 or key == ord('q'):
        break
    elif key == ord(' '):
        paused = not paused
    elif key == ord('s'):
        if paused and region.roi:
            # Calcular formatos YOLO
            x_min, x_max = min(region.roi[0], region.roi[2]), max(region.roi[0], region.roi[2])
            y_min, y_max = min(region.roi[1], region.roi[3]), max(region.roi[1], region.roi[3])
            
            x_center = ((x_min + x_max) / 2) / w
            y_center = ((y_min + y_max) / 2) / h
            box_w = (x_max - x_min) / w
            box_h = (y_max - y_min) / h
            
            # Limitar a bounds entre 0 y 1 por si te pasas dibujando fuera del marco
            x_center = max(0, min(1, x_center))
            y_center = max(0, min(1, y_center))
            box_w = max(0, min(1, box_w))
            box_h = max(0, min(1, box_h))
            
            # Guardamos la imagen
            N += 1
            img_path = os.path.join(IMG_DIR, f"obj_{N:04d}.jpg")
            lbl_path = os.path.join(LBL_DIR, f"obj_{N:04d}.txt")
            
            cv.imwrite(img_path, frame)
            with open(lbl_path, "w") as f:
                f.write(f"0 {x_center:.6f} {y_center:.6f} {box_w:.6f} {box_h:.6f}\n")
            
            print(f"[{N}] Creados {img_path} y {lbl_path}")
            
            # Reiniciar para seguir trabajando
            region.roi = []
            paused = False

    # Avanzar el frame si no está pausado
    if not paused:
        try:
            key_stream, frame = next(generador_stream)
        except StopIteration:
            # Si era un archivo de vídeo y se acabó, lo pausamos al final en vez de romper
            paused = True

print(f"\n¡Listo! Generaste {N} imágenes manualmente.")
cv.destroyAllWindows()
