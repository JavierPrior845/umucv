#!/usr/bin/env python

# Opcional 5: Sustitución de foto del DNI en tiempo real (AR)
#
# USO:
#   python opc5_dni.py --swap mi_foto.jpg
#

import cv2 as cv
import numpy as np
import argparse
import os
from umucv.stream import autoStream
from umucv.util  import putText, ROI     # ROI gestiona el mouse callback igual que el resto de la asignatura

# -------- Estado --------
estado     = "ESPERAR_REFERENCIA"
frame_ref  = None
kp_ref     = None
des_ref    = None
pts_roi_ref= None
img_swap   = None

sift = cv.SIFT_create(nfeatures=2000)
bf   = cv.BFMatcher()

VENTANA = "DNI AR"   # Nombre corto sin tildes ni caracteres especiales


def buscar_homografia(frame_actual):
    gray = cv.cvtColor(frame_actual, cv.COLOR_BGR2GRAY)
    kp_act, des_act = sift.detectAndCompute(gray, None)
    if des_act is None or len(des_act) < 10:
        return None
    matches = bf.knnMatch(des_ref, des_act, k=2)
    good = [m for m, n in matches if m.distance < 0.75 * n.distance]
    if len(good) < 15:
        return None
    src_pts = np.float32([kp_ref[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp_act[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
    H, mask = cv.findHomography(src_pts, dst_pts, cv.RANSAC, 5.0)
    if H is None:
        return None
    if mask is not None and mask.sum() < len(good) * 0.3:
        return None
    return H


def pegar_imagen_en_region(frame, pts_destino, img):
    h_img, w_img = img.shape[:2]
    pts_src = np.float32([[0,0],[w_img,0],[w_img,h_img],[0,h_img]])
    pts_dst = pts_destino.reshape(4,2).astype(np.float32)
    M = cv.getPerspectiveTransform(pts_src, pts_dst)
    h_f, w_f = frame.shape[:2]
    warped = cv.warpPerspective(img, M, (w_f, h_f))
    mask = np.zeros((h_f, w_f), dtype=np.uint8)
    cv.fillConvexPoly(mask, np.int32(pts_dst), 255)
    mask = cv.GaussianBlur(mask, (5,5), 3)
    mask_3ch = mask[:,:,np.newaxis] / 255.0
    return (frame.astype(np.float32)*(1-mask_3ch) + warped.astype(np.float32)*mask_3ch).astype(np.uint8)


# -------- Main --------
parser = argparse.ArgumentParser(description="Sustitucion de foto en DNI en tiempo real")
parser.add_argument('--swap', type=str, default=None, help="Imagen de sustitución")
args, _ = parser.parse_known_args()

if args.swap and os.path.exists(args.swap):
    img_swap = cv.imread(args.swap)
    print(f"Imagen cargada: {args.swap}")
else:
    img_swap = np.zeros((200,160,3), dtype=np.uint8)
    img_swap[:] = (50,150,50)
    cv.putText(img_swap, "SWAP", (20,110), cv.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 3)
    print("Sin --swap. Usando cuadrado verde de demo.")

# Crear ROI usando la clase de umucv (gestiona el callback del ratón correctamente)
region = ROI(VENTANA)

print("\n--- SUSTITUCION DE FOTO EN DNI ---")
print("1. Pon el DNI visible y pulsa 'c' para capturar referencia.")
print("2. Arrastra con el RATON un rectangulo sobre la FOTO del DNI.")
print("3. Pulsa ENTER para activar la sustitucion.")
print("Pulsa 'r' para reiniciar. Pulsa ESC para salir.\n")

for key, frame in autoStream():
    display = frame.copy()

    # ---- ESPERAR REFERENCIA ----
    if estado == "ESPERAR_REFERENCIA":
        putText(display, "DNI visible? Pulsa 'c' para capturar referencia", (10,30), color=(0,255,255))
        if key == ord('c'):
            frame_ref = frame.copy()
            gray_ref  = cv.cvtColor(frame_ref, cv.COLOR_BGR2GRAY)
            kp_ref, des_ref = sift.detectAndCompute(gray_ref, None)
            region.roi = []          # Limpiar ROI anterior
            estado = "MARCAR_REGION"
            print(f"Referencia capturada ({len(kp_ref)} kp). Dibuja el ROI sobre la foto del DNI.")

    # ---- MARCAR REGION ----
    elif estado == "MARCAR_REGION":
        display = frame_ref.copy()   # Mostramos el frame congelado para dibujar encima
        putText(display, "Arrastra ROI sobre la FOTO del DNI. ENTER para confirmar.", (10,30), color=(0,255,0))

        if region.roi:
            x1,y1,x2,y2 = region.roi
            cv.rectangle(display, (x1,y1), (x2,y2), (0,255,0), 2)

        if key == 13 and region.roi:   # ENTER
            x1,y1,x2,y2 = region.roi
            pts_roi_ref = np.float32([[x1,y1],[x2,y1],[x2,y2],[x1,y2]])
            estado = "ACTIVO"
            print("Sustitucion activa. Mueve la camara alrededor del DNI.")

    # ---- ACTIVO ----
    elif estado == "ACTIVO":
        H = buscar_homografia(frame)
        if H is not None:
            pts_act = cv.perspectiveTransform(pts_roi_ref.reshape(-1,1,2), H)
            display  = pegar_imagen_en_region(frame, pts_act, img_swap)
            cv.polylines(display, [np.int32(pts_act)], True, (0,255,0), 1)
            putText(display, "DNI detectado | Foto sustituida", (10,30), color=(0,255,0))
        else:
            putText(display, "DNI no detectado. Apunta al DNI.", (10,30), color=(0,0,255))

    # Reiniciar
    if key == ord('r'):
        estado = "ESPERAR_REFERENCIA"
        frame_ref = kp_ref = des_ref = pts_roi_ref = None
        region.roi = []
        print("Reiniciado.")

    cv.imshow(VENTANA, display)
    if key == 27:
        break

cv.destroyAllWindows()
