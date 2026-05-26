## 1. Errores Críticos y Fallos Potenciales de Código (Bugs Reales)

### El Bug del Kernel Fijo en el Desenfoque (Ejercicio 3)

En el fragmento de código de anonimización aplicas un filtro rígido:

```python
blur = cv.GaussianBlur(roi, (51, 51), 30)

```

* 
**El problema:** Si YOLOv11 detecta a una persona que se encuentra muy alejada de la cámara, las dimensiones de su caja delimitadora (*ROI*) pueden ser inferiores a 51x51 píxeles. En muchas versiones de OpenCV, intentar aplicar un kernel de convolución cuyas dimensiones superen el tamaño físico de la matriz de la imagen de entrada provoca un fallo de aserción (`Assertion failed`) interrumpiendo la ejecución del flujo de vídeo en tiempo real.


* **La solución:** Modifica el código para que el tamaño del kernel sea dinámico y proporcional al tamaño de la ROI (asegurando siempre que sea un número impar), o añade una salvaguarda que reescale la subimagen antes de aplicar el filtro si esta es demasiado pequeña.

### Omisión de Centrado en el Análisis de Procrustes (Ejercicio 4)

En el módulo `metodos.py` expones el cálculo de la matriz de covarianza cruzada para los landmarks de la mano:

```python
H = lm_frame.T @ lm_modelo

```

* **El problema:** El algoritmo de alineación de Procrustes (o algoritmo de Kabsch) para resolver la rotación óptima $R$ mediante la Descomposición en Valores Singulares (SVD) requiere de manera estricta que **ambas nubes de puntos estén centradas en el origen** (es decir, con sus respectivos centroides restados: $\mu = 0$). Si pasas las coordenadas tridimensionales crudas arrojadas por MediaPipe directamente a la multiplicación matricial, la traslación espacial de la mano respecto a la cámara corromperá la matriz $H$. Esto causará que la rotación extraída a través de la SVD sea errónea y varíe artificialmente según la posición de la mano en la pantalla.
* **La solución:** Asegúrate de restar la media de cada eje a `lm_frame` y `lm_modelo` antes de calcular su producto traspuéstor.

---

## 2. Omisiones Técnicas y Falta de Rigor Académico

### Falta de Especificaciones en la Calibración (Ejercicio 1)

* 
**Datos ausentes:** Mencionas un error RMS de 0.369 y muestras la matriz $K$ , pero omites detallar el tamaño real en milímetros de los cuadrados del tablero de ajedrez utilizado y el número total de capturas independientes que procesó el script `calibrate.py`. Para que el experimento sea reproducible (un requisito clave en cualquier revisión académica), estos parámetros deben constar de forma explícita.


* 
**Geometría de la cuadrícula:** En la sección 2.4 no aclaras si la proyección de las líneas virtuales se realiza sobre el flujo de vídeo crudo o desdistorsionado. Dado que calculaste unos coeficientes de distorsión radial no nulos ($k_1 \approx 0.0754$) , proyectar líneas rectas directas (`cv.line`) sobre una imagen con distorsión en barril provocará que la precisión geométrica se degrade notablemente en las periferias de la imagen. Deberías especificar si rectificas el frame previamente.



### Indefinición del Algoritmo de Tracking (Ejercicio 2)

* 
**Asociación de datos:** Explicas la heurística de conteo al cruzar la línea basándote en la comparación de `cy` y `vy` (coordenada actual e histórica), pero no detallas qué algoritmo utilizas para resolver el problema de la correspondencia temporal de los centroides entre fotogramas secuenciales. Si dos vehículos circulan en paralelo o cruzan la línea al mismo tiempo, el lector no sabe si empleas una asignación simple por distancia Euclídea mínima, el algoritmo de Munkres (Húngaro) o un Filtro de Kalman. Explicar este paso es fundamental.


* 
**Procesamiento morfológico:** Mencionas que aplicas procesamiento morfológico tras el sustractor MOG2, pero no especificas qué operaciones (ej. *Opening* para remover ruido aislado y *Closing* para rellenar los huecos de los bboxes) ni qué geometrías o tamaños de kernel has programado.



---

## 3. Sugerencias de Optimización e "Ingeniería de Producción"

### Eficiencia del Pipeline de Deep Learning (Ejercicio 5)

* 
**Análisis de latencia:** Documentas un tiempo de inferencia de 94.1 ms en una CPU AMD Ryzen 7 utilizando el modelo nano de YOLOv11 (`yolo11n.pt`). Para un modelo de ese tamaño en una CPU de arquitectura moderna, casi 100 ms es una marca de rendimiento mejorable que denota el uso de las librerías nativas de PyTorch sobre tensores de CPU sin optimizar.


* **Propuesta de mejora:** Para demostrar un perfil enfocado a la ingeniería de producción, añade una sección de "Trabajo Futuro" o "Optimización de Despliegue" donde propongas exportar el modelo entrenado `.pt` a formatos de ejecución optimizados como **ONNX Runtime** o **OpenVINO**, lo que reduciría la latencia de inferencia por debajo de los 20 ms en esa misma CPU.
* **Detalles del dataset:** Falta añadir un breve desglose cuantitativo de tu dataset personalizado: número de imágenes totales capturadas, cuántas se usaron para entrenamiento y cuántas para validación (el split habitual 80/20).

### Limitaciones de los Métodos Opcionales

* 
**Opcional 1 (Sobel Vectorizado):** Tu técnica de slicing matricial (`img[0:-2, 0:-2]`) no implementa estrategias de padding en las fronteras de la imagen. Como consecuencia colateral, el tamaño final de la imagen se reduce en 2 píxeles por cada dimensión (pasa de 640x480 a 638x478). Mencionar este efecto de borde y compararlo con el comportamiento de OpenCV (que usa replicación de bordes como `BORDER_DEFAULT`) enriquecerá el análisis del benchmark.


* 
**Opcional 2 (HCI Hand Control):** Tu cálculo del parámetro de profundidad basado en la distancia entre los nudillos del índice y el meñique presenta una vulnerabilidad geométrica inherente. Si el usuario inclina la mano hacia adelante o hacia atrás (cambios en el *pitch* o *yaw*), la proyección 2D de la palma se comprimirá en la imagen, engañando al sistema para que interprete una falsa acción de alejamiento (zoom out) sin que se haya modificado la distancia real del eje $Z$. Destacar este acoplamiento de grados de libertad demuestra una profunda comprensión del sistema físico.



---

## 4. Correcciones de Estilo y Notación en el Documento

* 
**Ortografía en la Introducción:** En la Sección 1, la frase *"explicación de como se han resuelto los ejercicios correspondientes a la practica..."* contiene dos erratas menores. Debe escribirse con acento: *"cómo se han resuelto"* (interrogativa indirecta) y *"práctica"*.


* 
**Estructura de referencias métricas (Ejercicio 6):** En el archivo `referencias.txt`, las dimensiones asignadas a las coordenadas del mundo real definen una disposición de 5.4 cm de ancho por 8.5 cm de alto. Aunque matemáticamente la homografía operará de forma idéntica, la orientación estándar del carnet de conducir (ISO 7810 ID-1) se lee de forma inversa (8.5 cm de ancho por 5.4 cm de alto). Revisa que las asignaciones de tus clics sigan rigurosamente el orden de los cuadrantes espaciales para evitar inversiones accidentales en el eje de coordenadas proyectado.
