#!/usr/bin/env python

# Opcional 6: Mosaico Automático con Homografías
# Crea automáticamente un panorama a partir de imágenes en una carpeta.
# No se asume ningún orden. Compara el resultado con cv.Stitcher.

import cv2 as cv
import numpy as np
import os
import argparse
from itertools import combinations

def encontrar_correspondencias(img1_gray, img2_gray, min_matches=10):
    """
    Encuentra correspondencias entre dos imágenes usando SIFT + Ratio Test.
    Devuelve (kp1, kp2, good_matches) o None si no hay suficientes.
    """
    sift = cv.SIFT_create(nfeatures=2000)
    kp1, des1 = sift.detectAndCompute(img1_gray, None)
    kp2, des2 = sift.detectAndCompute(img2_gray, None)

    if des1 is None or des2 is None or len(des1) < 2 or len(des2) < 2:
        return None

    bf = cv.BFMatcher()
    matches = bf.knnMatch(des1, des2, k=2)
    
    # Ratio test de Lowe
    good = [m for m, n in matches if m.distance < 0.75 * n.distance]
    
    if len(good) < min_matches:
        return None
    
    return kp1, kp2, good


def calcular_homografia(kp1, kp2, matches):
    """
    Calcula la homografía entre dos conjuntos de puntos usando RANSAC.
    """
    src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
    H, mask = cv.findHomography(src_pts, dst_pts, cv.RANSAC, 5.0)
    return H, mask


def crear_mosaico_manual(imagenes):
    """
    Crea un mosaico proyectando todas las imágenes al espacio de la imagen central.
    Construye un grafo de solapamientos y une las imágenes usando sus homografías.
    """
    n = len(imagenes)
    if n == 0:
        return None

    # Convertir a gris para las correspondencias
    grises = [cv.cvtColor(img, cv.COLOR_BGR2GRAY) for img in imagenes]
    
    # Construir grafo de homografías entre pares de imágenes que solapan
    # Clave: (i, j) -> H que lleva de img_i a img_j
    grafo_H = {}
    print("Buscando correspondencias entre pares de imágenes...")
    for i, j in combinations(range(n), 2):
        res = encontrar_correspondencias(grises[i], grises[j])
        if res is not None:
            kp1, kp2, good = res
            H, mask = calcular_homografia(kp1, kp2, good)
            if H is not None:
                grafo_H[(i, j)] = H
                grafo_H[(j, i)] = np.linalg.inv(H)
                print(f"  Solapamiento encontrado: img{i} <-> img{j} ({len(good)} matches)")

    if not grafo_H:
        print("No se encontraron solapamientos entre ningún par de imágenes.")
        return None

    # Usar la imagen central como referencia (índice n//2)
    ref = n // 2
    
    # BFS para calcular la homografía acumulada de cada imagen a la referencia
    H_global = {ref: np.eye(3)}
    visitados = {ref}
    cola = [ref]
    while cola:
        actual = cola.pop(0)
        for (i, j), H in grafo_H.items():
            if i == actual and j not in visitados:
                H_global[j] = H_global[actual] @ H
                visitados.add(j)
                cola.append(j)
    
    if len(H_global) < n:
        print(f"Advertencia: Solo se pudieron conectar {len(H_global)}/{n} imágenes.")

    # Estimar dimensiones del mosaico proyectando esquinas de cada imagen
    h_ref, w_ref = imagenes[ref].shape[:2]
    all_corners = []
    for idx, H in H_global.items():
        h, w = imagenes[idx].shape[:2]
        corners = np.float32([[0, 0], [w, 0], [w, h], [0, h]]).reshape(-1, 1, 2)
        corners_warp = cv.perspectiveTransform(corners, np.linalg.inv(H))
        all_corners.append(corners_warp.reshape(-1, 2))
    
    all_corners = np.vstack(all_corners)
    x_min, y_min = np.floor(all_corners.min(axis=0)).astype(int)
    x_max, y_max = np.ceil(all_corners.max(axis=0)).astype(int)
    
    # Offset para que todo quede en coordenadas positivas
    offset = np.array([[1, 0, -x_min],
                       [0, 1, -y_min],
                       [0, 0, 1]], dtype=np.float64)
    
    mosaic_w = x_max - x_min
    mosaic_h = y_max - y_min
    
    # Limitar el tamaño para no matar la memoria RAM
    scale = min(1.0, 4000 / max(mosaic_w, mosaic_h))
    mosaic_w = int(mosaic_w * scale)
    mosaic_h = int(mosaic_h * scale)
    
    mosaico = np.zeros((mosaic_h, mosaic_w, 3), dtype=np.uint8)
    
    # Proyectar cada imagen al mosaico (la de referencia al final para que quede nítida)
    orden = sorted(H_global.keys(), key=lambda x: x != ref)
    for idx in orden:
        H_final = offset @ np.linalg.inv(H_global[idx])
        # Escalar si hicimos resize
        if scale < 1.0:
            S = np.diag([scale, scale, 1.0])
            H_final = S @ H_final
        cv.warpPerspective(imagenes[idx], H_final, (mosaic_w, mosaic_h),
                           dst=mosaico, borderMode=cv.BORDER_TRANSPARENT)
    
    return mosaico


def main():
    parser = argparse.ArgumentParser(description="Mosaico automático con homografías")
    parser.add_argument('--dir', type=str, required=True, help="Directorio con las imágenes")
    parser.add_argument('--out', type=str, default="mosaico_resultado.jpg", help="Nombre del archivo de salida")
    args = parser.parse_args()

    # Cargar imágenes
    extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
    archivos = sorted([f for f in os.listdir(args.dir) if f.lower().endswith(extensions)])
    
    if len(archivos) < 2:
        print("Se necesitan al menos 2 imágenes en el directorio.")
        return
    
    print(f"Cargando {len(archivos)} imágenes de '{args.dir}'...")
    imagenes = []
    for f in archivos:
        img = cv.imread(os.path.join(args.dir, f))
        if img is not None:
            # Reducir para acelerar el proceso
            h, w = img.shape[:2]
            if w > 1200:
                img = cv.resize(img, (1200, int(h * 1200 / w)))
            imagenes.append(img)
    
    print(f"Imágenes cargadas: {len(imagenes)}")

    print("\n[1/2] Creando mosaico con Homografías manuales...")
    mosaico_manual = crear_mosaico_manual(imagenes)
    
    if mosaico_manual is not None:
        out_manual = args.out.replace('.', '_manual.')
        cv.imwrite(out_manual, mosaico_manual)
        print(f"Mosaico manual guardado en: {out_manual}")
        cv.imshow("Mosaico Manual (Homografias)", mosaico_manual)
    else:
        print("No se pudo crear el mosaico manual.")

    print("\n[2/2] Creando mosaico con cv.Stitcher (método nativo)...")
    stitcher = cv.Stitcher.create(cv.Stitcher_PANORAMA)
    status, mosaico_cv = stitcher.stitch(imagenes)
    
    if status == cv.Stitcher_OK:
        out_cv = args.out.replace('.', '_opencv.')
        cv.imwrite(out_cv, mosaico_cv)
        print(f"Mosaico OpenCV guardado en: {out_cv}")
        cv.imshow("Mosaico OpenCV (Stitcher)", mosaico_cv)
    else:
        print(f"cv.Stitcher falló con código: {status}")

    print("\nPulsa cualquier tecla para salir...")
    cv.waitKey(0)
    cv.destroyAllWindows()


if __name__ == "__main__":
    main()
