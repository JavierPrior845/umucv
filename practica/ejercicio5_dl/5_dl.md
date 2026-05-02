# Ejercicio 5: Entrenamiento de Deep Learning (Objeto Personalizado)

Este ejercicio demuestra el flujo completo para entrenar un modelo de detección de objetos personalizado utilizando **Ultralytics YOLOv11**, enseñándole a la red a detectar un objeto de tu elección (ej. tu ratón, una botella, una taza).

## Metodología

Entrenar un modelo desde cero requiere miles de imágenes etiquetadas a mano. Para este ejercicio prepararemos un dataset pequeño (unas 40 o 50 imágenes) y haremos "Fine-tuning" a un modelo pre-entrenado.

### 1. Etiquetado Manual (`preparar_dataset.py`)
He diseñado este script para que sea comodísimo crear tu propio dataset directamente usando tu cámara u origen de video.
- **Funcionamiento Dinámico**: El vídeo se reproduce en tiempo real. Cuando veas tu objeto claro, pulsa la **BARRA ESPACIADORA** para pausar el frame.
- **Dibuja**: Arrastra con el ratón dibujando un cuadradito rojo alrededor de tu objeto.
- **Pulsa 's'**: Al pulsar la S, se guarda la foto y un archivo `.txt` con las coordenadas YOLO exactas, y el vídeo se despausa solo para que busques el siguiente ángulo.

> **💡 Consejo sobre Orígenes**: Puedes usar la webcam, o si prefieres, grabar un clip de 15 segundos con tu móvil dando vueltas al objeto, pasar el `video.mp4` al PC, y ejecutar `python preparar_dataset.py --dev video.mp4`.


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
    Una vez terminado, puedes usar la herramienta de línea de comandos preinstalada de YOLO para probar tu modelo `best.pt` con la misma cámara:
    ```bash
    yolo detect predict model=runs/detect/train/weights/best.pt source=0 show=True
    ```

## Resultados del Entrenamiento

He ejecutado un entrenamiento de validación de concepto con los siguientes resultados:
- **Modelo Base**: YOLOv11 Nano (`yolo11n.pt`).
- **Épocas**: 10.
- **Rendimiento Final**: La métrica **mAP50 alcanzó un 0.995** al finalizar la validación, indicando que la caja delimitadora tiene una confianza superior al 99% de acierto al encuadrar el objeto en los contextos probados.
- **Velocidad de Inferencia**: En CPU AMD Ryzen, el modelo procesa imágenes a un ritmo de ~94 ms por foto. Esto equivale a más de **10 imágenes por segundo (10 FPS)**, lo cual es ideal para procesamiento de vídeo en tiempo real sin requerir aceleración GPU masiva.
- **Modelo Resultante**: Los pesos optimizados se han generado en `runs/detect/train4/weights/best.pt` con un tamaño sumamente ligero de 5.4MB.
