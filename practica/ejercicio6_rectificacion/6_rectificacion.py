#!/usr/bin/env python

import cv2 as cv
import numpy as np
import argparse
import sys
import math
from umucv.util import putText

# Variables globales para la interaccion del raton
puntos_usuario = []
H = None  # Matriz de homografia

def cargar_referencias(ruta_ref):
    """
    Lee el archivo de texto con las referencias.
    Formato esperado por linea: img_x img_y real_x real_y
    """
    src_pts = []
    dst_pts = []
    try:
        with open(ruta_ref, 'r') as f:
            for linea in f:
                partes = linea.strip().split()
                if len(partes) == 4:
                    ix, iy, rx, ry = map(float, partes)
                    src_pts.append([ix, iy])
                    dst_pts.append([rx, ry])
    except Exception as e:
        print(f"Error al leer el archivo de referencias: {e}")
        sys.exit(1)
        
    if len(src_pts) < 4:
        print("Se necesitan al menos 4 puntos en el archivo de referencia para calcular la homografía.")
        sys.exit(1)
        
    return np.array(src_pts, dtype=np.float32), np.array(dst_pts, dtype=np.float32)


def manejador_raton(event, x, y, flags, param):
    """Maneja los clics del usuario en la imagen."""
    global puntos_usuario
    
    if event == cv.EVENT_LBUTTONDOWN:
        puntos_usuario.append((x, y))
        # Guardamos solo los dos ultimos clics
        if len(puntos_usuario) > 2:
            puntos_usuario.pop(0)


def calcular_distancia_real(p1_img, p2_img, matriz_H):
    """
    Transforma dos puntos de la imagen al plano real usando H
    y calcula la distancia euclídea entre ellos.
    """
    # Convertir a formato compatible con perspectiveTransform: [[[x, y]], [[x, y]]]
    pts = np.array([[p1_img], [p2_img]], dtype=np.float32)
    
    # Proyectar al plano real
    pts_reales = cv.perspectiveTransform(pts, matriz_H)
    
    # Extraer coordenadas
    rx1, ry1 = pts_reales[0][0]
    rx2, ry2 = pts_reales[1][0]
    
    # Distancia Euclidiana
    dist = math.sqrt((rx2 - rx1)**2 + (ry2 - ry1)**2)
    return dist


def main():
    global H, puntos_usuario
    
    parser = argparse.ArgumentParser(description="Medición en imagen rectificada.")
    parser.add_argument('--image', required=True, help="Ruta de la imagen de entrada")
    parser.add_argument('--ref', required=True, help="Ruta al archivo TXT con las referencias")
    args = parser.parse_args()

    # 1. Cargar imagen
    img_original = cv.imread(args.image)
    if img_original is None:
        print(f"No se pudo cargar la imagen: {args.image}")
        sys.exit(1)

    # 2. Cargar puntos y calcular Homografia
    src_pts, dst_pts = cargar_referencias(args.ref)
    # findHomography es mas robusto que getPerspectiveTransform si hay > 4 puntos
    H, status = cv.findHomography(src_pts, dst_pts, cv.RANSAC)
    
    if H is None:
        print("No se pudo encontrar una homografía válida con los puntos proporcionados.")
        sys.exit(1)

    # Configurar interfaz
    ventana_nombre = "Rectificacion - Click para medir"
    cv.namedWindow(ventana_nombre)
    cv.setMouseCallback(ventana_nombre, manejador_raton)

    print("\n--- HERRAMIENTA DE MEDICIÓN MEDIANTE RECTIFICACIÓN ---")
    print("Homografía calculada correctamente.")
    print("Instrucciones:")
    print(" - Haz CLICK IZQUIERDO en dos puntos de la imagen para medir la distancia real.")
    print(" - Presiona 'q' o 'ESC' para salir.\n")

    while True:
        frame = img_original.copy()
        
        # Dibujar puntos de calibracion originales como guia (en amarillo)
        for pt in src_pts:
            cv.circle(frame, (int(pt[0]), int(pt[1])), 4, (0, 255, 255), -1)
            
        # Dibujar interaccion del usuario
        for pt in puntos_usuario:
            cv.circle(frame, pt, 5, (0, 0, 255), -1)
            
        if len(puntos_usuario) == 2:
            p1 = puntos_usuario[0]
            p2 = puntos_usuario[1]
            # Linea de conexion
            cv.line(frame, p1, p2, (0, 255, 0), 2)
            
            # Calculo de distancia real
            dist_real = calcular_distancia_real(p1, p2, H)
            
            # Mostrar resultado en medio de la linea y arriba a la izquierda
            px_medio = (p1[0] + p2[0]) // 2
            py_medio = (p1[1] + p2[1]) // 2
            
            texto_dist = f"{dist_real:.2f} unidades"
            cv.putText(frame, texto_dist, (px_medio, py_medio - 10), 
                       cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv.putText(frame, texto_dist, (px_medio, py_medio - 10), 
                       cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
                       
            putText(frame, f"Distancia medida: {texto_dist}", (10, 30), color=(0, 255, 0), div=2)
        else:
            putText(frame, "Haz click en dos puntos para medir", (10, 30), color=(255, 255, 255), div=2)

        cv.imshow(ventana_nombre, frame)
        
        key = cv.waitKey(30) & 0xFF
        if key == 27 or key == ord('q'):
            break

    cv.destroyAllWindows()

if __name__ == "__main__":
    main()
