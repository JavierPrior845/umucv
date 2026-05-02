#!/usr/bin/env python

import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
from umucv.stream import autoStream
from collections import defaultdict
import time

# Substractor de fondo
bgsub = cv.createBackgroundSubtractorMOG2(history=500, varThreshold=25, detectShadows=True)

# Parámetros para el conteo
LINE_Y = 250   # Línea horizontal que usarán los coches para ser contados
MIN_AREA = 300 # Área mínima para considerar que es un vehículo

# Variables para seguimiento simple (centroides)
# id_vehiculo -> (x, y)
vehiculos_activos = {}
siguiente_id = 0

# Contadores
conteo_bajada = 0
conteo_subida = 0

# Historial para las gráficas: guardaremos (timestamp, sentido)
registro_eventos = []

# Tiempos para saber los FPS
t0 = time.time()
frames = 0

print("INSTRUCCIONES:")
print("Abre este script usando: python 2_trafico.py --dev carretera")
print("Pulsa 'q' o 'ESC' para salir y generar la gráfica de tráfico.")

for key, frame in autoStream():
    h, w = frame.shape[:2]
    frames += 1
    
    # 1. Aplicamos sustracción de fondo
    fgmask = bgsub.apply(frame)
    
    # 2. Eliminamos sombras (el MOG2 las marca con 127) y binarizamos
    _, fgmask = cv.threshold(fgmask, 200, 255, cv.THRESH_BINARY)
    
    # 3. Operaciones morfológicas para rellenar huecos y quitar ruido
    kernel_erode = np.ones((3,3), np.uint8)
    kernel_dilate = np.ones((7,7), np.uint8)
    
    fgmask = cv.erode(fgmask, kernel_erode, iterations=1)
    fgmask = cv.dilate(fgmask, kernel_dilate, iterations=2)
    
    # 4. Encontrar contornos
    contornos, _ = cv.findContours(fgmask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    
    centroides_actuales = []
    
    for c in contornos:
        if cv.contourArea(c) > MIN_AREA:
            x, y, w_box, h_box = cv.boundingRect(c)
            # Centroide del bounding box
            cx = x + w_box // 2
            cy = y + h_box // 2
            centroides_actuales.append((cx, cy, w_box, h_box))
            
            # Dibujar el rectángulo
            cv.rectangle(frame, (x, y), (x + w_box, y + h_box), (0, 255, 255), 2)
    
    # 5. Tracking simple: asociar centroides actuales con los anteriores por proximidad
    nuevos_vehiculos = {}
    usados = set()
    
    for vid, (vx, vy) in vehiculos_activos.items():
        # Buscar el centroide más cercano en el frame actual
        mejor_dist = float('inf')
        mejor_cd = None
        
        for i, (cx, cy, w_box, h_box) in enumerate(centroides_actuales):
            if i in usados:
                continue
            dist = np.hypot(cx - vx, cy - vy)
            if dist < 50 and dist < mejor_dist: # Umbral de distancia (en píxeles) de salto entre frames
                mejor_dist = dist
                mejor_cd = (i, cx, cy)
                
        if mejor_cd is not None:
            i, cx, cy = mejor_cd
            nuevos_vehiculos[vid] = (cx, cy)
            usados.add(i)
            
            # 6. Lógica de Conteo
            # Si el vehículo cruza la LÍNEA_Y
            # Bajada: Y anterior < LINE_Y y Y nuevo >= LINE_Y
            if vy < LINE_Y and cy >= LINE_Y:
                conteo_bajada += 1
                registro_eventos.append((time.time(), 'bajada'))
                cv.circle(frame, (cx, cy), 15, (0, 0, 255), -1) # Flash al contar
            # Subida: Y anterior > LINE_Y y Y nuevo <= LINE_Y
            elif vy > LINE_Y and cy <= LINE_Y:
                conteo_subida += 1
                registro_eventos.append((time.time(), 'subida'))
                cv.circle(frame, (cx, cy), 15, (0, 255, 0), -1)

    for i, (cx, cy, w_box, h_box) in enumerate(centroides_actuales):
        if i not in usados:
            nuevos_vehiculos[siguiente_id] = (cx, cy)
            siguiente_id += 1
            
    vehiculos_activos = nuevos_vehiculos
    
    # 7. Interfaz gráfica
    cv.line(frame, (0, LINE_Y), (w, LINE_Y), (255, 0, 0), 2)
    
    cv.putText(frame, f"Bajada: {conteo_bajada}", (10, 30), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
    cv.putText(frame, f"Subida: {conteo_subida}", (10, 70), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
    
    cv.imshow('Trafico', frame)
    cv.imshow('Mascara', fgmask)
    
    if key == 27 or key == ord('q'):
        break

cv.destroyAllWindows()

# --- Generación de Gráficas ---
if len(registro_eventos) > 0:
    print("Generando gráfica de tráfico...")
    t_inicial = registro_eventos[0][0]
    
    tiempos_bajada = [t - t_inicial for t, d in registro_eventos if d == 'bajada']
    tiempos_subida = [t - t_inicial for t, d in registro_eventos if d == 'subida']
    
    plt.figure(figsize=(10, 5))
    
    BINS = max(1, int((time.time() - t_inicial) / 5))
    
    plt.hist(tiempos_bajada, bins=BINS, alpha=0.5, color='red', label='Bajada')
    plt.hist(tiempos_subida, bins=BINS, alpha=0.5, color='green', label='Subida')
    
    plt.title("Flujo de Tráfico por Tiempo")
    plt.xlabel("Tiempo (segundos)")
    plt.ylabel("Número de Vehículos detectados")
    plt.legend()
    
    plt.savefig('grafica_trafico.png')
    print("Gráfica guardada como 'grafica_trafico.png'.")
    plt.show()    
else:
    print("No se registraron vehículos cruzando la línea (o el script se cerró muy pronto).")
