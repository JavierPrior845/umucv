#!/usr/bin/env python

import cv2 as cv
import numpy as np
import time
from umucv.stream import autoStream
from umucv.util import putText

def sobel_manual(image):
    """
    Implementación propia del operador Sobel usando Numpy puro (sin cv.filter2D).
    Se optimiza usando slicing de arrays en lugar de bucles for, 
    pero manteniendo la matemática explícita subyacente.
    """
    # Convertir a escala de grises y flotante
    if len(image.shape) == 3:
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY).astype(np.float32)
    else:
        gray = image.astype(np.float32)

    # Padding para no salirnos de los bordes (1 pixel alrededor)
    padded = np.pad(gray, 1, mode='edge')
    
    # Matrices de Sobel
    # Kx = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
    # Ky = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]

    # Extraer "vistas" desplazadas de la imagen para vectorizar el cálculo
    # Esto simula un deslizamiento de la ventana 3x3 por toda la imagen simultáneamente.
    top_left     = padded[:-2, :-2]
    top_mid      = padded[:-2, 1:-1]
    top_right    = padded[:-2, 2:]
    mid_left     = padded[1:-1, :-2]
    mid_right    = padded[1:-1, 2:]
    bottom_left  = padded[2:, :-2]
    bottom_mid   = padded[2:, 1:-1]
    bottom_right = padded[2:, 2:]

    # Convolución Gx
    gx = (-1 * top_left) + (1 * top_right) + \
         (-2 * mid_left) + (2 * mid_right) + \
         (-1 * bottom_left) + (1 * bottom_right)

    # Convolución Gy
    gy = (-1 * top_left) + (-2 * top_mid) + (-1 * top_right) + \
         (1 * bottom_left) + (2 * bottom_mid) + (1 * bottom_right)

    # Magnitud del gradiente
    magnitude = np.sqrt(gx**2 + gy**2)
    
    # Normalizar a 0-255 y convertir a uint8
    magnitude = np.clip(magnitude, 0, 255).astype(np.uint8)
    return magnitude

def sobel_opencv(image):
    """
    Implementación nativa altamente optimizada en C++ de OpenCV.
    """
    if len(image.shape) == 3:
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    else:
        gray = image
        
    gx = cv.Sobel(gray, cv.CV_32F, 1, 0, ksize=3)
    gy = cv.Sobel(gray, cv.CV_32F, 0, 1, ksize=3)
    
    magnitude = cv.magnitude(gx, gy)
    magnitude = np.clip(magnitude, 0, 255).astype(np.uint8)
    return magnitude

print("\n--- COMPARATIVA DE RENDIMIENTO: SOBEL MANUAL vs OPENCV ---")
print("Observa los FPS (Fotogramas por Segundo) en la esquina superior.")
print("Pulsa 'ESC' para salir.\n")

for key, frame in autoStream():
    # Reducimos un poco el tamaño si la imagen es muy grande para no hundir a Python
    h, w = frame.shape[:2]
    if w > 800:
        frame = cv.resize(frame, (800, int(h * 800 / w)))
        
    t0 = time.time()
    res_manual = sobel_manual(frame)
    t1 = time.time()
    fps_manual = 1.0 / (t1 - t0) if (t1 - t0) > 0 else 999

    t2 = time.time()
    res_opencv = sobel_opencv(frame)
    t3 = time.time()
    fps_opencv = 1.0 / (t3 - t2) if (t3 - t2) > 0 else 999

    # Convertir a BGR para poner texto en color
    res_manual_color = cv.cvtColor(res_manual, cv.COLOR_GRAY2BGR)
    res_opencv_color = cv.cvtColor(res_opencv, cv.COLOR_GRAY2BGR)

    putText(res_manual_color, f"SOBEL PYTHON (NUMPY)", (10, 30), color=(0, 255, 255))
    putText(res_manual_color, f"FPS: {fps_manual:.1f} ({1000*(t1-t0):.1f} ms)", (10, 60), color=(0, 255, 255))

    putText(res_opencv_color, f"SOBEL NATIVO (OPENCV)", (10, 30), color=(0, 255, 0))
    putText(res_opencv_color, f"FPS: {fps_opencv:.1f} ({1000*(t3-t2):.1f} ms)", (10, 60), color=(0, 255, 0))

    # Concatenar horizontalmente
    combined = np.hstack((res_manual_color, res_opencv_color))
    
    cv.imshow("Comparativa Algoritmos", combined)

    if key == 27 or key == ord('q'):
        break

cv.destroyAllWindows()
