#!/usr/bin/env python

import cv2 as cv
import argparse

def manejador_raton(event, x, y, flags, param):
    if event == cv.EVENT_LBUTTONDOWN:
        print(f"{x} {y}")

def main():
    parser = argparse.ArgumentParser(description="Haz clic en la imagen para obtener las coordenadas de los píxeles.")
    parser.add_argument('--image', required=True, help="Ruta de la imagen de entrada")
    args = parser.parse_args()

    img = cv.imread(args.image)
    if img is None:
        print(f"No se pudo cargar la imagen: {args.image}")
        return

    ventana_nombre = "Haz clic en las 4 esquinas - ESC para salir"
    cv.namedWindow(ventana_nombre)
    cv.setMouseCallback(ventana_nombre, manejador_raton)

    print("\nHaz clic en los puntos de la imagen para ver sus coordenadas (X Y) en esta consola.")
    print("Presiona la tecla ESC para cerrar la ventana cuando termines.\n")

    while True:
        cv.imshow(ventana_nombre, img)
        key = cv.waitKey(30) & 0xFF
        if key == 27 or key == ord('q'):
            break

    cv.destroyAllWindows()

if __name__ == "__main__":
    main()
