#!/usr/bin/env python

import cv2 as cv
import numpy as np
import os
import argparse
from umucv.stream import autoStream, sourceArgs
from umucv.util import putText
import metodos

def main():
    # 1. Configuración de Argumentos
    parser = argparse.ArgumentParser(description="Clasificador de Imágenes Modular")
    sourceArgs(parser)
    parser.add_argument('--models', type=str, required=True, help="Carpeta de modelos")
    parser.add_argument('--method', type=str, required=True, choices=['sift', 'embedder', 'manos'], 
                        help="Método de comparación")
    args, _ = parser.parse_known_args()

    # 2. Inicializar el método seleccionado
    if args.method == 'sift':
        engine = metodos.MetodoSIFT()
    elif args.method == 'embedder':
        engine = metodos.MetodoEmbedder()
    elif args.method == 'manos':
        engine = metodos.MetodoManos()

    # 3. Cargar modelos existentes
    os.makedirs(args.models, exist_ok=True)
    modelos_db = {} # nombre_archivo -> descriptor_precomputado

    def cargar_modelos():
        modelos_db.clear()
        files = [f for f in os.listdir(args.models) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        print(f"Cargando {len(files)} modelos desde {args.models}...")
        for f in files:
            path = os.path.join(args.models, f)
            img = cv.imread(path)
            if img is not None:
                desc = engine.preprocesar_modelo(img)
                if desc is not None:
                    modelos_db[f] = desc
        print("Carga finalizada.")

    cargar_modelos()

    # 4. Bucle Principal
    print(f"\nCLASIFICADOR ACTIVO (Método: {args.method})")
    print("Capturando video... Pulsa 'c' para capturar el frame actual como NUEVO MODELO.")
    print("Pulsa 'q' o 'ESC' para salir.\n")

    for key, frame in autoStream():
        # A. Capturar nuevo modelo
        if key == ord('c'):
            nombre = f"modelo_{len(modelos_db)}.png"
            path = os.path.join(args.models, nombre)
            cv.imwrite(path, frame)
            print(f"Nuevo modelo guardado: {nombre}")
            # Re-procesar para añadirlo a la DB sin recargar todo
            desc = engine.preprocesar_modelo(frame)
            if desc is not None:
                modelos_db[nombre] = desc

        # B. Procesar frame actual
        try:
            desc_frame = engine.procesar_frame(frame)
        except Exception as e:
            desc_frame = None

        # C. Comparar con base de datos
        mejor_match = "Ninguino"
        mejor_score = float('inf')

        if desc_frame is not None:
            for nombre, desc_modelo in modelos_db.items():
                score = engine.comparar(desc_frame, desc_modelo)
                # print(f"Comparando con {nombre}: {score}")
                if score < mejor_score:
                    mejor_score = score
                    mejor_match = nombre

        # D. Visualización
        h, w = frame.shape[:2]
        # Umbrales heurísticos para mostrar texto de confianza (personalizables)
        confianza_visual = ""
        if args.method == 'sift' and mejor_score < -15:
             confianza_visual = f" (Matches: {-mejor_score})"
        elif args.method == 'embedder' and mejor_score < 0.2:
             confianza_visual = f" (Dist: {mejor_score:.3f})"
        elif args.method == 'manos' and mejor_score < 0.15:
             confianza_visual = f" (Dist: {mejor_score:.3f})"
        else:
             mejor_match = "Incierto..."

        texto = f"Metodo: {args.method.upper()} | Modelos: {len(modelos_db)}"
        putText(frame, texto, (10, 30), color=(255, 255, 255), div=2)
        
        res_text = f"Resultado: {mejor_match}{confianza_visual}"
        color_res = (0, 255, 0) if "Incierto" not in mejor_match else (0, 0, 255)
        putText(frame, res_text, (10, 70), color=color_res, div=2)

        cv.imshow('Clasificador Modular', frame)

        if key == 27 or key == ord('q'):
            break

    cv.destroyAllWindows()

if __name__ == "__main__":
    main()
