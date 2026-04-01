#!/usr/bin/env python

import cv2 as cv
import numpy as np
import os
from umucv.stream import autoStream

# Variables globales que atacan a las trackbars.
# Inicializamos a que estamos a una altura H=15 (por ej. decimetros -> 1.5m)
# Y a una distancia de la pared Z=40 (decimetros -> 4.0m)
params = {
    'H': 15,
    'Z': 40,
    'GridSize': 5
}

def update_val(name):
    def f(val):
        # Evitar ceros para no dividir por cero en Z
        if val == 0 and name == 'Z':
            val = 1
        params[name] = val
    return f

cv.namedWindow('Grid')
cv.createTrackbar('H (dm)', 'Grid', params['H'], 30, update_val('H'))
cv.createTrackbar('Z (dm)', 'Grid', params['Z'], 200, update_val('Z'))
cv.createTrackbar('Grid Space (dm)','Grid', params['GridSize'], 20, update_val('GridSize'))

# Intentar cargar una calibración si existe, de lo contrario usamos valores aproximados por defecto.
K = np.array([
    [500., 0., 320.],
    [0., 500., 240.],
    [0., 0., 1.]
])

calib_path = os.path.join(os.path.dirname(__file__), 'calib.txt')
if os.path.exists(calib_path):
    try:
        calib = np.loadtxt(calib_path)
        K = calib[:9].reshape(3, 3)
        print(f"Calibración cargada desde {calib_path}")
    except Exception as e:
        print("No se pudo cargar calib.txt, usando cámara ideal.")
else:
    print("calib.txt no encontrado, usando cámara ideal de 640x480 con FOV medio.")

fx, fy = K[0, 0], K[1, 1]
cx, cy = K[0, 2], K[1, 2]

for key, frame in autoStream():
    # Obtener el W y H de la cámara
    h_img, w_img = frame.shape[:2]
    
    H_real = params['H'] # dm
    Z_real = params['Z'] # dm
    step = params['GridSize']
    if step == 0:
        step = 1

    # Línea del horizonte (C_y de la camara, asumiendo cámara horizontal)
    horizon_y = int(cy)
    cv.line(frame, (0, horizon_y), (w_img, horizon_y), (150, 150, 150), 2)
    cv.putText(frame, 'Horizonte', (10, horizon_y - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)

    # Coordenada en plano imagen para el encuentro 'pared' vs 'suelo' (basado en el modelo pinhole)
    # y = f_y * (Y / Z) + c_y -> donde el Y en camara es H (suelo)
    base_y = int(fy * (H_real / Z_real) + cy)
    cv.line(frame, (0, base_y), (w_img, base_y), (0, 0, 255), 3)

    # --- Dibujar cuadrícula en la "pared" (Plano Z perpendicular a la cámara) ---
    # El eje X va de izquierda a derecha.
    # El eje Y va de arriba a abajo. (Suelo es Y = H_real)
    
    # Líneas verticales sobre el plano a distancia Z_real.
    # Recorremos la habitación en X buscando valores múltiples del paso (step).
    X_min, X_max = -50, 50 # Ancho de 5 metros a cada lado de la cámara.
    for x_real in range(X_min, X_max + step, step):
        # Punto inicial de la línea: Arriba de la habitación, p.ej. techo (Y = -H_real)
        # Punto final de la línea: Suelo (Y = H_real)
        y_img_suelo = int(fy * (H_real / Z_real) + cy)
        y_img_techo = int(fy * (-H_real / Z_real) + cy)
        
        x_img = int(fx * (x_real / Z_real) + cx)
        
        if 0 <= x_img <= w_img:
            cv.line(frame, (x_img, y_img_techo), (x_img, y_img_suelo), (0, 255, 0), 1)

    # Líneas horizontales sobre el plano a distancia Z_real.
    # Recorremos desde el techo (-H_real) al suelo (H_real).
    for y_real in range(-int(H_real), int(H_real) + step, step):
        # Calculamos la proyeción en Y
        y_img = int(fy * (y_real / Z_real) + cy)
        
        # Proyectamos desde el extremo izquierdo de la habitación al extremo derecho
        x_img_izq = int(fx * (X_min / Z_real) + cx)
        x_img_der = int(fx * (X_max / Z_real) + cx)
        
        if 0 <= y_img <= h_img:
             cv.line(frame, (x_img_izq, y_img), (x_img_der, y_img), (0, 255, 0), 1)

    cv.imshow('Grid', frame)

    if key == 27: # Esc para salir
        break

cv.destroyAllWindows()
