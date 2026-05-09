#!/usr/bin/env python

# Opcional 7: Realidad Aumentada con objetos virtuales desplazados con el ratón.
# El usuario hace click en un punto del plano detectado y un objeto virtual
# se "pega" en ese punto en coordenadas del mundo, siguiendo el movimiento de la cámara.

import cv2 as cv
import numpy as np
import argparse
from umucv.stream import autoStream
from umucv.util import putText

# --- ESTADO GLOBAL ---
objetos_virtuales = []  # Lista de objetos: {'pos_mundo': (x,y), 'color': ..., 'radio': ...}

# Colores disponibles para los objetos
COLORES = [
    (0, 100, 255),   # Naranja
    (255, 50, 50),   # Azul
    (50, 200, 50),   # Verde
    (200, 50, 200),  # Magenta
    (50, 200, 200),  # Amarillo
]
color_actual = [0]

# Homografía del plano detectado (se actualiza en cada frame)
H_plano = [None]

def callback_raton(event, x, y, flags, param):
    """
    Al hacer clic izquierdo, si tenemos una homografía calculada,
    proyectamos el punto del clic al plano 2D del mundo y guardamos el objeto.
    """
    if event == cv.EVENT_LBUTTONDOWN:
        if H_plano[0] is not None:
            # Transformar punto imagen -> punto mundo usando la homografía inversa
            pt = np.array([[[x, y]]], dtype=np.float32)
            pt_mundo = cv.perspectiveTransform(pt, H_plano[0])
            wx, wy = pt_mundo[0][0]
            color = COLORES[color_actual[0] % len(COLORES)]
            objetos_virtuales.append({'pos_mundo': (wx, wy), 'color': color, 'radio': 20})
            color_actual[0] += 1
            print(f"Objeto añadido en el mundo: ({wx:.1f}, {wy:.1f})")
        else:
            print("Sin plano de referencia. Muestra el marcador/tablero primero.")


def detectar_tablero_ajedrez(frame, patron=(7, 5)):
    """
    Intenta detectar un tablero de ajedrez para establecer el plano de referencia.
    Devuelve (H_img_to_mundo, H_mundo_to_img) o (None, None).
    """
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    ret, corners = cv.findChessboardCorners(gray, patron, None)
    
    if not ret:
        return None, None
    
    # Refinar esquinas subpixélicas
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    corners = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
    
    # Puntos del "mundo" en cm (el tablero tiene cuadros de 1 unidad)
    rows, cols = patron[1], patron[0]
    world_pts = np.float32([[c, r] for r in range(rows) for c in range(cols)])
    img_pts = corners.reshape(-1, 2)
    
    # Homografía imagen -> mundo y mundo -> imagen
    H_i2w, _ = cv.findHomography(img_pts, world_pts)
    H_w2i, _ = cv.findHomography(world_pts, img_pts)
    
    return H_i2w, H_w2i


def proyectar_objeto(frame, pos_mundo, color, radio, H_w2i):
    """
    Dibuja un círculo en la imagen en la posición correspondiente al punto del mundo.
    """
    pt = np.array([[[pos_mundo[0], pos_mundo[1]]]], dtype=np.float32)
    pt_img = cv.perspectiveTransform(pt, H_w2i)
    px, py = int(pt_img[0][0][0]), int(pt_img[0][0][1])
    
    h, w = frame.shape[:2]
    if 0 <= px < w and 0 <= py < h:
        cv.circle(frame, (px, py), radio, color, -1)
        cv.circle(frame, (px, py), radio, (255, 255, 255), 2)  # Borde blanco


# --- MAIN ---
parser = argparse.ArgumentParser(description="AR - Objetos virtuales con ratón")
parser.add_argument('--patron', type=str, default='7x5',
                    help="Tamaño del patrón de ajedrez (columnas x filas, default: 7x5)")
args, _ = parser.parse_known_args()

# Parsear el patrón
try:
    cols, rows = map(int, args.patron.split('x'))
    patron = (cols, rows)
except:
    patron = (7, 5)

cv.namedWindow("AR Objetos Virtuales")
cv.setMouseCallback("AR Objetos Virtuales", callback_raton)

print("\n--- REALIDAD AUMENTADA: OBJETOS VIRTUALES ---")
print(f"Mostrando patrón de ajedrez ({patron[0]}x{patron[1]}) a la cámara.")
print("Una vez detectado, haz CLICK en cualquier punto del tablero para poner un objeto.")
print("Pulsa 'c' para limpiar todos los objetos.")
print("Pulsa 'q' o ESC para salir.\n")

H_w2i = None

for key, frame in autoStream():
    display = frame.copy()
    
    # Intentar detectar el tablero en cada frame
    H_i2w, H_w2i_nuevo = detectar_tablero_ajedrez(frame, patron)
    
    if H_w2i_nuevo is not None:
        H_plano[0] = H_i2w    # Actualizar la H para convertir clics -> mundo
        H_w2i = H_w2i_nuevo   # Actualizar la H para proyectar objetos -> imagen
        
        # Dibujar los ejes del plano detectado como referencia visual
        esquinas_mundo = np.float32([[0, 0], [4, 0], [4, 3], [0, 3]]).reshape(-1, 1, 2)
        esquinas_img = cv.perspectiveTransform(esquinas_mundo, H_w2i)
        cv.polylines(display, [np.int32(esquinas_img)], True, (0, 255, 0), 2)
        putText(display, "Plano detectado. Haz click para añadir objetos.", (10, 30), color=(0, 255, 0))
    else:
        putText(display, f"Buscando tablero {patron[0]}x{patron[1]}...", (10, 30), color=(0, 0, 255))
    
    # Limpiar objetos
    if key == ord('c'):
        objetos_virtuales.clear()
        print("Objetos borrados.")
    
    # Proyectar los objetos guardados sobre la imagen actual
    if H_w2i is not None:
        for obj in objetos_virtuales:
            proyectar_objeto(display, obj['pos_mundo'], obj['color'], obj['radio'], H_w2i)
    
    putText(display, f"Objetos: {len(objetos_virtuales)} | Pulsa 'c' para borrar", (10, 60))
    cv.imshow("AR Objetos Virtuales", display)
    
    if key == 27 or key == ord('q'):
        break

cv.destroyAllWindows()
