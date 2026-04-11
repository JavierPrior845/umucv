# Ejercicio 5: Entrenamiento de Modelo Deep Learning (Boca)

Este ejercicio demuestra el flujo completo para entrenar un modelo de detección de objetos personalizado utilizando **Ultralytics YOLOv11**.

## Metodología

Entrenar un modelo desde cero requiere miles de imágenes etiquetadas a mano. Para hacer este ejercicio de forma eficiente y rápida, hemos optado por un **auto-etiquetador** basado en MediaPipe.

### 1. Captura de Datos (`preparar_dataset.py`)
Este script utiliza la cámara y el modelo pre-entrenado de **MediaPipe Face Mesh** para localizar los puntos clave de la boca.
- **Auto-etiquetado**: Automáticamente calcula el rectángulo que envuelve la boca y guarda las coordenadas en el formato que necesita YOLO (`.txt`).
- **Diversidad**: Captura una imagen cada segundo. Debes moverte, gesticular y variar la iluminación para que el modelo sea robusto.

### 2. Configuración (`data.yaml`)
Define la estructura de carpetas y el nombre de la clase (0: boca) para que el entrenador sepa qué está aprendiendo.

### 3. Entrenamiento (`train_yolo.py`)
Utiliza la librería `ultralytics` para cargar el modelo `yolo11n.pt` (nano) y realizar el "Fine-tuning" con tus imágenes.
- Se han configurado **100 épocas** y aumentos de datos (volteos, cambios de brillo) para mejorar el resultado.
- El modelo final se guardará en una carpeta llamada `runs/detect/train/weights/best.pt`.

## Instrucciones Paso a Paso

1.  **Captura imágenes de entrenamiento**:
    ```bash
    python preparar_dataset.py
    ```
    Muévete frente a la cámara unos 30-60 segundos para tener unas 50 imágenes.
    
2.  **Preparar Validación**:
    Copia 2 o 3 imágenes de `train/images/` a `val/images/` y sus correspondientes archivos `.txt` de `train/labels/` a `val/labels/`. Esto es necesario para que YOLO evalúe su progreso.

3.  **Lanzar el entrenamiento**:
    ```bash
    python train_yolo.py
    ```
    *Nota: Si tienes una tarjeta gráfica NVIDIA, puedes editar el script y poner `device=0` para que sea mucho más rápido.*

4.  **Probar el modelo**:
    Una vez terminado, puedes usar el script de ejemplo de la asignatura para probar tu modelo `best.pt`:
    ```bash
    # (Ejemplo de comando de inferencia)
    yolo detect predict model=runs/detect/train/weights/best.pt source=0 show=True
    ```
