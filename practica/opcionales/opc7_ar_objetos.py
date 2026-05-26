#!/usr/bin/env python

# Opcional 7: Realidad Aumentada con objetos virtuales desplazados con el ratón.
# El usuario hace click en un punto del plano detectado y un objeto virtual
# se "pega" en ese punto en coordenadas del mundo (Z=0), siguiendo el movimiento de la cámara.
# Soporta tanto círculos 2D proyectados en perspectiva como cubos 3D mediante pose.

import cv2 as cv
import numpy as np
import argparse
import os
import math
from umucv.stream import autoStream
from umucv.util import putText
from umucv.htrans import Pose, htrans, Kfov

objetos_virtuales = []  # Lista de objetos: {'pos_mundo': (x,y), 'color': ..., 'radio_mundo': ...}
mode = [0]             # 0: Círculos 2D con perspectiva, 1: Cubos 3D por pose

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
    proyectamos el punto del clic al plano 2D del mundo (Z=0) y guardamos el objeto.
    """
    if event == cv.EVENT_LBUTTONDOWN:
        if H_plano[0] is not None:
            # Transformar punto imagen -> punto mundo usando la homografía inversa
            pt = np.array([[[x, y]]], dtype=np.float32)
            pt_mundo = cv.perspectiveTransform(pt, H_plano[0])
            wx, wy = pt_mundo[0][0]
            color = COLORES[color_actual[0] % len(COLORES)]
            # Guardamos el objeto con un radio de 0.4 unidades del mundo (tamaño de la cuadrícula)
            objetos_virtuales.append({'pos_mundo': (wx, wy), 'color': color, 'radio_mundo': 0.4})
            color_actual[0] += 1
            print(f"Objeto añadido en coordenadas del mundo: ({wx:.2f}, {wy:.2f})")
        else:
            print("Sin plano de referencia. Muestra el marcador/tablero primero.")


def detectar_tablero_ajedrez(frame, patron=(7, 5)):
    """
    Intenta detectar un tablero de ajedrez para establecer el plano de referencia.
    Optimizado: realiza la búsqueda rápida a baja resolución y soporta rotación (transpuesta) del patrón.
    Devuelve (H_img_to_mundo, H_mundo_to_img, corners_full_res, patron_activo) o (None, None, None, None).
    """
    h, w = frame.shape[:2]
    scale_factor = 0.5
    small_w = int(w * scale_factor)
    small_h = int(h * scale_factor)
    
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    gray_small = cv.resize(gray, (small_w, small_h))
    
    flags = cv.CALIB_CB_ADAPTIVE_THRESH + cv.CALIB_CB_FAST_CHECK
    ret, corners = cv.findChessboardCorners(gray_small, patron, flags)
    active_patron = patron
    
    if not ret:
        patron_inv = (patron[1], patron[0])
        ret, corners = cv.findChessboardCorners(gray_small, patron_inv, flags)
        if not ret:
            return None, None, None, None
        active_patron = patron_inv
        
    # Escalar esquinas de vuelta a resolución completa
    corners = corners / scale_factor
    
    # Refinar esquinas subpixélicas sobre la imagen de alta resolución (muy rápido)
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    corners = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
    
    cols, rows = active_patron[0], active_patron[1]
    world_pts = np.float32([[c, r] for r in range(rows) for c in range(cols)])
    img_pts = corners.reshape(-1, 2)
    
    # Homografías resultantes
    H_i2w, _ = cv.findHomography(img_pts, world_pts)
    H_w2i, _ = cv.findHomography(world_pts, img_pts)
    
    return H_i2w, H_w2i, img_pts, active_patron


def proyectar_circulo_perspectiva(frame, pos_mundo, color, radio_mundo, H_w2i):
    """
    Dibuja un círculo plano sobre el tablero en coordenadas del mundo.
    El tamaño del círculo se escala en perspectiva de acuerdo a la distancia a la cámara.
    """
    wx, wy = pos_mundo
    # Centro proyectado
    pt_c = np.array([[[wx, wy]]], dtype=np.float32)
    pt_c_img = cv.perspectiveTransform(pt_c, H_w2i)
    px, py = int(pt_c_img[0][0][0]), int(pt_c_img[0][0][1])
    
    # Punto en el borde exterior del círculo en el plano (desplazado en el eje X real)
    pt_r = np.array([[[wx + radio_mundo, wy]]], dtype=np.float32)
    pt_r_img = cv.perspectiveTransform(pt_r, H_w2i)
    bx, by = int(pt_r_img[0][0][0]), int(pt_r_img[0][0][1])
    
    # El radio en píxeles es la distancia entre el centro y el borde proyectados
    radio_px = int(np.hypot(bx - px, by - py))
    
    h, w = frame.shape[:2]
    if 0 <= px < w and 0 <= py < h and radio_px > 0:
        cv.circle(frame, (px, py), radio_px, color, -1, cv.LINE_AA)
        cv.circle(frame, (px, py), radio_px, (255, 255, 255), 2, cv.LINE_AA)  # Borde blanco


def proyectar_cubo_3d(frame, pos_mundo, color, pose_cam, size_cube=0.8):
    """
    Proyecta y dibuja un cubo 3D sobre el plano utilizando la pose estimada.
    """
    wx, wy = pos_mundo
    s = size_cube / 2
    
    # Vértices del cubo en el espacio 3D (Z negativo es hacia arriba, saliendo del tablero)
    vertices = np.array([
        [wx - s, wy - s, 0],
        [wx + s, wy - s, 0],
        [wx + s, wy + s, 0],
        [wx - s, wy + s, 0],
        [wx - s, wy - s, -size_cube],
        [wx + s, wy - s, -size_cube],
        [wx + s, wy + s, -size_cube],
        [wx - s, wy + s, -size_cube]
    ])
    
    # Proyectar los puntos a la imagen usando la matriz M de la pose (M = K @ [R|t])
    pts_img = htrans(pose_cam.M, vertices)
    pts_img = np.int32(pts_img)
    
    # Sombreado semitransparente para dar volumen
    overlay = frame.copy()
    # Rellenar caras laterales, base y tapa
    cv.drawContours(overlay, [pts_img[:4]], -1, color, -1)
    cv.drawContours(overlay, [pts_img[4:]], -1, color, -1)
    for i in range(4):
        cara = np.array([pts_img[i], pts_img[(i+1)%4], pts_img[(i+1)%4 + 4], pts_img[i+4]])
        cv.drawContours(overlay, [cara], -1, color, -1)
    cv.addWeighted(overlay, 0.20, frame, 0.80, 0, frame)
    
    # Dibujar líneas de las aristas del cubo
    cv.drawContours(frame, [pts_img[:4]], -1, color, 2, cv.LINE_AA)
    cv.drawContours(frame, [pts_img[4:]], -1, color, 2, cv.LINE_AA)
    for i in range(4):
        cv.line(frame, tuple(pts_img[i]), tuple(pts_img[i+4]), color, 2, cv.LINE_AA)
        
    # Dibujar el contorno del cubo en blanco para perfilarlo
    cv.drawContours(frame, [pts_img[:4]], -1, (255, 255, 255), 1, cv.LINE_AA)
    cv.drawContours(frame, [pts_img[4:]], -1, (255, 255, 255), 1, cv.LINE_AA)


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
print("Una vez detectado, haz CLICK en cualquier punto del tablero para colocar un objeto.")
print("Pulsa 'm' para cambiar entre círculos 2D y cubos 3D.")
print("Pulsa 'c' para limpiar todos los objetos.")
print("Pulsa 'q' o ESC para salir.\n")

# Intentar cargar la matriz K desde calib.txt
K = None
calib_path = 'practica/ejercicio1_calibracion/calib.txt'
if not os.path.exists(calib_path):
    calib_path = os.path.join(os.path.dirname(__file__), '../ejercicio1_calibracion/calib.txt')

if os.path.exists(calib_path):
    try:
        calib = np.loadtxt(calib_path)
        K = calib[:9].reshape(3, 3)
        print(f"Calibración de cámara cargada desde {calib_path}")
    except Exception as e:
        print(f"Error al cargar calib.txt: {e}. Se estimará la focal en base a resolución.")

H_w2i = None

for key, frame in autoStream():
    display = frame.copy()
    h_frame, w_frame = frame.shape[:2]
    
    # Inicializar K aproximada si no pudimos cargar calib.txt
    if K is None:
        K = Kfov((w_frame, h_frame), 60)
        print(f"Focal estimada (FOV 60°). Matriz K:\n{K}")
    
    # Intentar detectar el tablero
    H_i2w, H_w2i_nuevo, img_pts, active_patron = detectar_tablero_ajedrez(frame, patron)
    
    if H_w2i_nuevo is not None:
        H_plano[0] = H_i2w
        H_w2i = H_w2i_nuevo
        cols_det, rows_det = active_patron
        
        # Estimar Pose 3D de la cámara usando el helper de umucv
        world_pts_pose = np.float32([[c, r] for r in range(rows_det) for c in range(cols_det)])
        pose_cam = Pose(K, img_pts, world_pts_pose)
        
        if pose_cam.rms < 5.0:  # Comprobamos que el error de reproyección sea aceptable
            # Ejes de tamaño 2.0 unidades del tablero
            ejes_3d = np.array([
                [0, 0, 0],
                [2.0, 0, 0],
                [0, 2.0, 0],
                [0, 0, -2.0]
            ])
            ejes_img = htrans(pose_cam.M, ejes_3d)
            origin = tuple(np.int32(ejes_img[0]))
            ax_x = tuple(np.int32(ejes_img[1]))
            ax_y = tuple(np.int32(ejes_img[2]))
            ax_z = tuple(np.int32(ejes_img[3]))
            
            cv.line(display, origin, ax_x, (0, 0, 255), 3, cv.LINE_AA)  # X: Rojo
            cv.line(display, origin, ax_y, (0, 255, 0), 3, cv.LINE_AA)  # Y: Verde
            cv.line(display, origin, ax_z, (255, 0, 0), 3, cv.LINE_AA)  # Z: Azul
            
            esquinas_mundo = np.float32([
                [0, 0, 0],
                [cols_det - 1, 0, 0],
                [cols_det - 1, rows_det - 1, 0],
                [0, rows_det - 1, 0]
            ])
            esquinas_img = htrans(pose_cam.M, esquinas_mundo)
            cv.polylines(display, [np.int32(esquinas_img)], True, (0, 255, 0), 2, cv.LINE_AA)
            
            for obj in objetos_virtuales:
                if mode[0] == 0:
                    proyectar_circulo_perspectiva(display, obj['pos_mundo'], obj['color'], obj['radio_mundo'], H_w2i)
                else:
                    proyectar_cubo_3d(display, obj['pos_mundo'], obj['color'], pose_cam, size_cube=0.8)
                    
            putText(display, "Plano detectado. Click para colocar.", (10, 30), color=(0, 255, 0))
        else:
            putText(display, f"Error en pose (RMS: {pose_cam.rms:.2f})", (10, 30), color=(0, 0, 255))
    else:
        putText(display, f"Buscando tablero {patron[0]}x{patron[1]}...", (10, 30), color=(0, 0, 255))
        # Si se pierde el tracking temporalmente, pintamos los objetos fijos en su última
        # posición conocida en la imagen (para evitar parpadeos molestos si la cámara está estática)
        if H_w2i is not None and mode[0] == 0:
            for obj in objetos_virtuales:
                # Pintar con transparencia o colores desvaídos para indicar pérdida de tracking
                proyectar_circulo_perspectiva(display, obj['pos_mundo'], (100, 100, 100), obj['radio_mundo'], H_w2i)
    
    # Alternar modo con la tecla 'm'
    if key == ord('m'):
        mode[0] = 1 - mode[0]
        mode_str = "3D (Cubos)" if mode[0] == 1 else "2D (Circulos)"
        print(f"Modo cambiado a: {mode_str}")
        
    # Limpiar objetos
    if key == ord('c'):
        objetos_virtuales.clear()
        print("Objetos borrados.")
    
    mode_str = "3D (Cubos)" if mode[0] == 1 else "2D (Circulos)"
    info_texto = f"Modo: {mode_str} ('m') | Objetos: {len(objetos_virtuales)} ('c' limpiar)"
    putText(display, info_texto, (10, 60))
    cv.imshow("AR Objetos Virtuales", display)
    
    if key == 27 or key == ord('q'):
        break

cv.destroyAllWindows()
