# Ejercicio 3: Actividad (Detector de Movimiento)

Este ejercicio consiste en crear un sistema de vigilancia inteligente que detecte movimiento en una zona específica, clasifique el objeto detectado y realice acciones automáticas como grabar un clip o enviar una notificación.

## Descripción del Problema
1.  **Región de Interés (ROI)**: El usuario debe poder marcar manualmente una zona de la imagen donde se quiere vigilar. El movimiento fuera de esta zona debe ser ignorado.
2.  **Detector de Movimiento**: Identificar cambios significativos en la ROI.
3.  **Grabación**: Si hay movimiento, guardar 2-3 segundos de vídeo.
4.  **Clasificación**: Determinar qué tipo de objeto ha causado el movimiento (usando técnicas de clasificación o detección).
5.  **Notificación**: Si el objeto pertenece a una categoría de interés (ej. "persona", "perro"), enviar una alerta (mensaje/foto) a un dispositivo móvil (ej. Telegram).
6.  **Anonimización**: Si se detectan personas, sus rostros o cuerpos deben ser pixelados o borrados para cumplir con la privacidad.

## Ideas para la Resolución

### 1. Selección de ROI
En la asignatura disponemos de `umucv.util.ROI`. Podemos usarlo para que el usuario dibuje un rectángulo con el ratón al inicio de la ejecución.
- **Referencia**: `code/util/roi.py` muestra cómo capturar eventos de ratón para definir áreas.

### 2. Detección de Movimiento
Podemos reutilizar la técnica del ejercicio anterior (**Background Subtraction**) pero limitada exclusivamente a los píxeles dentro de la ROI.
- Si el número de píxeles blancos en la máscara (dentro del ROI) supera un umbral, disparamos el evento "Movimiento Detectado".

### 3. Clasificación y Detección (Machine Learning)
Para saber *qué* se mueve, lo más eficiente hoy en día es usar un modelo preentrenado como **YOLO** (You Only Look Once) o **MediaPipe**.
- **YOLOv8/v11**: Muy rápido y preciso para detectar personas, coches, gatos, etc.
- **Referencia**: `code/DL/yolo/yolo.py` utiliza la librería `ultralytics` para detección en tiempo real.

### 4. Anonimización (Privacidad)
Si el clasificador detecta una `persona`, podemos aplicar un filtro a su bounding box:
- `frame[y1:y2, x1:x2] = cv2.GaussianBlur(frame[y1:y2, x1:x2], (51, 51), 0)`
- O reducir la resolución de esa zona y volver a ampliarla para dar un efecto de pixelado.

### 5. Grabación de Vídeo
Para guardar el clip de 2-3 segundos, podemos usar `cv2.VideoWriter`. Una idea es mantener un pequeño buffer de frames para incluir el segundo *antes* de que empezara el movimiento.

### 6. Notificaciones (Telegram Bot)
Crear un bot en Telegram es sencillo usando `python-telegram-bot` o simplemente peticiones `requests` a la API de Telegram:
- `https://api.telegram.org/bot<TOKEN>/sendPhoto?chat_id=<ID>`
- El token y el chat_id se pueden configurar como variables de entorno o en un archivo de configuración.

## Flujo Lógico Propuesto (Draft)
```python
# 1. Definir ROI (interactivo o fijo)
# 2. Bucle principal:
#    a. Restar fondo en ROI.
#    b. Si Movimiento > Umbral:
#       i. Iniciar grabación.
#       ii. Pasar frame a YOLO.
#       iii. Si clase == "interes":
#            - Anonimizar si es persona.
#            - Preparar notificación.
#    c. Si evento termina:
#       - Cerrar video y enviar notificación.
```
