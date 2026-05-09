#!/usr/bin/env python

# Opcional 3: Tracker de Lucas-Kanade con Ego-Motion
# Extensión de lk_track.py para estimar el movimiento de la cámara (Ego-Motion)
# y la velocidad angular aproximada.

import cv2 as cv
import numpy as np
import time
from collections import deque
from umucv.stream import autoStream
from umucv.util import putText

tracks = []
track_len = 10
detect_interval = 5

corners_params = dict(maxCorners=500, qualityLevel=0.1, minDistance=10, blockSize=7)
lk_params = dict(winSize=(15, 15), maxLevel=2, criteria=(cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 0.03))

# FOV horizontal estimado en grados para una webcam estándar
FOV_H = 60.0 

prevgray = None

print("\n--- ESTIMADOR DE EGO-MOTION (LUCAS-KANADE) ---")
print("Mueve la cámara en diferentes direcciones.")
print("Pulsa 'ESC' para salir.\n")

for n, (key, frame) in enumerate(autoStream()):
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    h, w = frame.shape[:2]
    cx, cy = w / 2.0, h / 2.0

    t0 = time.time()
    
    estado_camara = "ESTATICO"
    vel_angular = 0.0

    if tracks and prevgray is not None:
        p0 = np.float32([t[-1] for t in tracks])
        p1, _, _ = cv.calcOpticalFlowPyrLK(prevgray, gray, p0, None, **lk_params)
        p0r, _, _ = cv.calcOpticalFlowPyrLK(gray, prevgray, p1, None, **lk_params)
        d = abs(p0 - p0r).reshape(-1, 2).max(axis=1)
        good = d < 1

        new_tracks = []
        desplazamientos = []
        expansiones = []

        for t, pt_antiguo, pt_nuevo, ok in zip(tracks, p0.reshape(-1, 2), p1.reshape(-1, 2), good):
            if not ok:
                continue
            
            t.append(pt_nuevo)
            new_tracks.append(t)
            
            # Vector de desplazamiento del píxel
            dx = pt_nuevo[0] - pt_antiguo[0]
            dy = pt_nuevo[1] - pt_antiguo[1]
            desplazamientos.append((dx, dy))

            # Vector desde el centro de la imagen hasta el punto antiguo
            vec_c_x = pt_antiguo[0] - cx
            vec_c_y = pt_antiguo[1] - cy
            # Normalizamos el vector del centro para proyectar
            norma_c = np.hypot(vec_c_x, vec_c_y)
            if norma_c > 0:
                # Producto escalar para ver si el desplazamiento va en la misma direccion que el vector radial
                dot_product = (dx * vec_c_x + dy * vec_c_y) / norma_c
                expansiones.append(dot_product)

        tracks = new_tracks

        # Dibujar trayectorias
        cv.polylines(frame, [np.int32(t) for t in tracks], isClosed=False, color=(0, 150, 255))
        for t in tracks:
            cv.circle(frame, center=np.int32(t[-1]), radius=2, color=(0, 0, 255), thickness=-1)

        # -- ANALIZAR EGO-MOTION --
        if len(desplazamientos) > 5:
            # Desplazamiento promedio
            mean_dx = np.mean([d[0] for d in desplazamientos])
            mean_dy = np.mean([d[1] for d in desplazamientos])
            
            # Expansion promedio (positiva = acercamiento, negativa = alejamiento)
            mean_exp = np.mean(expansiones)

            # Umbrales heurísticos para decidir el estado
            umbral_mov = 1.0
            umbral_exp = 0.5

            if mean_exp > umbral_exp:
                estado_camara = "FORWARD (Avanzando)"
            elif mean_exp < -umbral_exp:
                estado_camara = "BACKWARD (Retrocediendo)"
            elif abs(mean_dx) > abs(mean_dy):
                if mean_dx > umbral_mov:
                    estado_camara = "LEFT (Puntos a Dcha)"
                elif mean_dx < -umbral_mov:
                    estado_camara = "RIGHT (Puntos a Izq)"
            else:
                if mean_dy > umbral_mov:
                    estado_camara = "UP (Puntos a Abajo)"
                elif mean_dy < -umbral_mov:
                    estado_camara = "DOWN (Puntos Arriba)"

            # -- VELOCIDAD ANGULAR --
            # FPS actual aproximado
            fps = 1.0 / (time.time() - t0) if time.time() - t0 > 0 else 30
            # Grados por píxel
            grados_per_pixel = FOV_H / w
            # Velocidad en X (pixels / frame) * (frames / segundo) * (grados / pixel)
            vel_angular = -mean_dx * fps * grados_per_pixel

    t1 = time.time()

    if n % detect_interval == 0:
        mask = np.zeros_like(gray)
        mask[:] = 255
        for x, y in [np.int32(t[-1]) for t in tracks]:
            cv.circle(mask, (int(x), int(y)), 5, 0, -1)
        corners = cv.goodFeaturesToTrack(gray, mask=mask, **corners_params)
        if corners is not None:
            for [pt] in np.float32(corners):
                tracks.append(deque([pt], maxlen=track_len))

    # UI
    putText(frame, f'EGO-MOTION: {estado_camara}', (10, 30), color=(0, 255, 0), scale=1.2, div=2)
    putText(frame, f'Velocidad Angular: {vel_angular:.1f} deg/s', (10, 60), color=(0, 255, 255))
    putText(frame, f'Tracks: {len(tracks)}', (10, h - 20), color=(200, 200, 200))

    cv.imshow('Ego-Motion Tracker', frame)
    prevgray = gray

    if key == 27 or key == ord('q'):
        break

cv.destroyAllWindows()
