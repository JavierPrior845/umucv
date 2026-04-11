#!/usr/bin/env python

from ultralytics import YOLO
import os

# Configuración
DATA_YAML = "data.yaml"
EPOCHS = 100
IMG_SIZE = 640

def main():
    if not os.path.exists(DATA_YAML):
        print(f"Error: No se encuentra el archivo {DATA_YAML}")
        return

    # 1. Cargar el modelo base (YOLOv11n es el más ligero)
    print("Cargando modelo base YOLOv11 nano...")
    model = YOLO("yolo11n.pt")

    # 2. Entrenar
    print(f"Iniciando entrenamiento por {EPOCHS} épocas...")
    results = model.train(
        data=DATA_YAML,
        epochs=EPOCHS,
        imgsz=IMG_SIZE,
        device="cpu", # Cambiar a '0' si tienes GPU NVIDIA
        augment=True
    )

    print("\n¡Entrenamiento completado!")
    print(f"El mejor modelo se ha guardado en: {results.save_dir}/weights/best.pt")

if __name__ == "__main__":
    main()
