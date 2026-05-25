# AUDITORÍA Y PROPUESTAS DE AMPLIACIÓN DE LA PRÁCTICA

## I. EJERCICIOS OBLIGATORIOS (1 - 6)

### Ejercicio 1: Calibración
* **Estado actual**: Se documenta la matriz $K$, el RMS de la calibración, los ángulos FOV y la lógica de proyección de la cuadrícula interactiva.
* **Qué cambiaría en el código**:
  * Implementar un conmutador interactivo (p. ej. tecla `d`) para mostrar el frame original frente al frame **corregido de distorsión** en tiempo real (`cv.undistort`).
* **Qué añadiría en la memoria**:
  * **Análisis de coeficientes de distorsión**: Detallar los coeficientes radiales ($k_1, k_2, k_3$) y tangenciales ($p_1, p_2$) obtenidos en la calibración y explicar físicamente qué tipo de deformación sufre tu lente (si es distorsión en barril o en cojín).
  * **Gráfica de error de reproyección**: Añadir una gráfica de barras con el error de reproyección medio por cada una de las imágenes de tablero de ajedrez utilizadas para calibrar, justificando si alguna foto con RMS muy alto fue descartada del dataset final.
* **Qué falta**: Una comparación visual (lado a lado) de una línea recta de la habitación antes y después de aplicar la corrección de distorsión.

### Ejercicio 2: Análisis de Tráfico
* **Estado actual**: Segmentación por sustracción de fondo (MOG2), control por centroides cruzando una línea e histograma de densidad al salir.
* **Qué cambiaría en el código**:
  * **Supresión de sombras**: OpenCV permite configurar `detectShadows=True` en `createBackgroundSubtractorMOG2`. Se puede mejorar el código filtrando las sombras (píxeles grises con bajo contraste en el canal de valor de HSV) para que las sombras de los vehículos no distorsionen los centroides ni fundan dos coches juntos.
  * **Rastreador clásico (Tracking)**: En vez de contar directamente por cruce de línea en un frame aislado, implementar un rastreador básico (por distancia euclídea entre centroides en fotogramas sucesivos o filtro de Kalman) para dar estabilidad si la máscara del coche sufre parpadeo o oclusión parcial.
* **Qué añadiría en la memoria**:
  * **Discusión sobre oclusiones y cambios de iluminación**: Explicar qué ocurre cuando pasa un camión grande tapando a un coche pequeño (oclusión por perspectiva), o cómo influyen los faros por la noche o los cambios climáticos repentinos (nubes/claros) en la velocidad de aprendizaje adaptativo de MOG2.
* **Qué falta**: Delimitar el conteo por sentido de la marcha de forma explícita en la interfaz (carril izquierdo vs carril derecho).

### Ejercicio 3: Videovigilancia (Actividad)
* **Estado actual**: Detección de movimiento en ROI, grabación secuencial de 2-3 s, filtro YOLO, anonimización por difuminado y alerta vía Telegram.
* **Qué cambiaría en el código**:
  * **Debounce / Temporizador de enfriamiento**: Añadir un retardo o *cooldown* (p. ej., 10 segundos) después de disparar una alerta de Telegram para evitar que el bot envíe spam masivo de mensajes si hay movimiento continuo.
  * **Clasificación localizada**: Pasar al detector de YOLO solo el recorte (*crop*) del ROI en lugar del frame completo para ahorrar ciclos de CPU.
* **Qué añadiría en la memoria**:
  * **Justificación ética y legal (RGPD)**: Un apartado corto sobre el Reglamento General de Protección de Datos (RGPD) en sistemas de vigilancia públicos, justificando por qué es técnicamente obligatorio anonimizar las caras y matrículas capturadas antes de ser enviadas a través de redes de terceros como Telegram.
* **Qué falta**: Modular el nivel de alerta según la ROI (p. ej., zona peatonal = aviso de cortesía; zona restringida = alerta crítica).

### Ejercicio 4: Clasificador Modular
* **Estado actual**: Reconocedor con SIFT (keypoints), MobileNetV3 (embeddings) y Análisis de Procrustes (hand landmarks).
* **Qué cambiaría en el código**:
  * **Precomputación y serialización**: Guardar los descriptores SIFT y embeddings calculados en disco (en formato `.pkl` o `.json`) para no tener que procesar la base de datos de imágenes de modelos cada vez que arranca el programa.
  * **Verificación geométrica**: En el módulo SIFT, en lugar de contar emparejamientos directos, realizar un filtro RANSAC para verificar si los matches configuran una homografía coherente. Esto elimina falsos positivos en fondos ruidosos.
* **Qué añadiría en la memoria**:
  * **Comparativa conceptual**: Una tabla comparando SIFT (geometría clásica local), Embedders (semántica profunda global) y Procrustes (estructura esquelética paramétrica), indicando los puntos fuertes y débiles de cada método ante cambios de iluminación, oclusión y rotación.
* **Qué falta**: Una interfaz interactiva mínima que permita guardar un objeto enfocado como "nuevo modelo" pulsando una tecla.

### Ejercicio 5: Deep Learning (YOLO)
* **Estado actual**: Fine-tuning de YOLO en un dataset propio, guardado de pesos e inferencia.
* **Qué cambiaría en el código**:
  * **Exportación del modelo**: Añadir instrucciones en el código para exportar el modelo `.pt` entrenado a formato ONNX o TensorRT para acelerar la velocidad de inferencia en dispositivos embebidos (CPU o placas tipo Raspberry Pi).
* **Qué añadiría en la memoria**:
  * **Técnicas de Data Augmentation**: Detallar qué transformaciones geométricas (rotación, escala, recorte) y fotométricas (brillo, ruido, contraste) aplicaste a tus imágenes para evitar el sobreentrenamiento (overfitting) dado el tamaño reducido del dataset.
  * **Análisis de Curvas**: Comentar los gráficos de pérdida (*loss curves*), curva de Precision-Recall y la matriz de confusión generadas automáticamente en la carpeta de entrenamiento de Ultralytics.
* **Qué falta**: Un análisis cuantitativo de los FPS alcanzados durante la inferencia en tiempo real en tu máquina.

### Ejercicio 6: Rectificación y Medición
* **Estado actual**: Calibración con homografía a partir de carnet, script de marcado de píxeles, medición interactiva de distancias en el plano y análisis de la oclusión 3D (botella).
* **Qué cambiaría en el código**:
  * **Integración del calibrador intrínseco (K)**: En lugar de usar la imagen distorsionada en bruto, pasar la imagen por la corrección de distorsión radial de la lente (del Ejercicio 1) antes de calcular la homografía. Esto corregirá la curvatura en los extremos de la imagen, donde las mediciones suelen fallar por unos milímetros.
  * **Generación de la vista rectificada**: Añadir una tecla (p. ej., `w`) que proyecte y guarde la imagen completamente aplanada (`cv.warpPerspective`) con las dimensiones reales correctas.
* **Qué añadiría en la memoria**:
  * **Derivación de la Homografía Inversa**: Incluir el desarrollo matemático de cómo se despeja el plano del mundo a partir de la inversa de la homografía y las coordenadas homogéneas.
* **Qué falta**: Comprobar el error absoluto medio (MAE) midiendo varios objetos de control y tabulando los resultados para calcular el porcentaje de error de la homografía según la distancia al origen.

---

## II. EJERCICIOS OPCIONALES (1 - 8)

### Opcional 1: Implementación de Sobel
* **Estado actual**: Convolución vectorizada por matrices desplazadas en Numpy vs OpenCV.
* **Qué cambiaría en el código**:
  * El código solo calcula la magnitud del gradiente. Se puede extender para calcular la orientación del gradiente (mediante `np.arctan2(gy, gx)`) y pintar los bordes coloreados según su dirección (codificación por colores HSV).
* **Qué añadiría en la memoria**:
  * **Ampliación teórica**: Explicar matemáticamente por qué el filtrado con Sobel actúa como una derivada discreta suavizada (convolución con el núcleo $[1, 2, 1]^T$ para suavizar y $[-1, 0, 1]$ para derivar).
* **Qué falta**: Implementar los pasos de la supresión de no máximos (NMS) y el umbralizado por histéresis para convertir tu mapa de Sobel en bordes finos de un solo píxel (emulando un detector de Canny completo).

### Opcional 2: Controlador Sin Contacto
* **Estado actual**: Detección de mano con MediaPipe, obtención de rotación por ángulo muñeca-corazón y escala por distancia de nudillos.
* **Qué cambiaría en el código**:
  * **Filtro de suavizado temporal**: Las coordenadas obtenidas de MediaPipe sufren de micro-vibración (*jitter*). Implementar una media móvil simple (SMA) o un filtro de suavizado exponencial (EMA) para estabilizar la rotación y la escala del polígono virtual.
  * **Eventos por gestos**: Utilizar la distancia de la punta de los dedos índice y pulgar para activar un evento discreto de "Click / Grab" (arrastrar el objeto por la pantalla) cuando la distancia sea inferior a un umbral (gesto de pinza).
* **Qué añadiría en la memoria**:
  * **Análisis de robustez ante oclusiones**: Explicar qué ocurre cuando la mano se gira lateralmente y se ocluyen los nudillos de referencia (meñique e índice), perdiendo momentáneamente el cálculo de escala.
* **Qué falta**: Mapear la posición de la mano para mover el centro del polígono por la pantalla (añadiendo dos grados de libertad traslacionales $X, Y$).

### Opcional 3: Ego-Motion (Lucas-Kanade)
* **Estado actual**: Dirección del movimiento por vectores de flujo promedio, estimación radial por producto escalar y velocidad angular usando FOV.
* **Qué cambiaría en el código**:
  * **Filtrado RANSAC de vectores**: Si un objeto dinámico cruza la pantalla (p. ej., pasa una persona caminando mientras mueves la cámara), su movimiento perturba el promedio de flujo. Implementar un filtro robusto (RANSAC o mediana) para descartar los vectores dinámicos (atípicos) y conservar solo el flujo de fondo estático.
* **Qué añadiría en la memoria**:
  * **El problema de la apertura**: Documentar a nivel teórico el *Aperture Problem* en flujo óptico y justificar por qué es necesario utilizar esquinas (como el detector de Shi-Tomasi) en lugar de bordes continuos para calcular el movimiento.
* **Qué falta**: Integrar la velocidad angular calculada a lo largo del tiempo para trazar de forma acumulativa un gráfico 2D simplificado de la trayectoria/odometría recorrida por la cámara.

### Opcional 4: Sudoku AR
* **Estado actual**: Contornos con Canny, bird-eye transform, lectura con Tesseract OCR (PSM 10), resolución lógica por backtracking y proyección por homografía inversa.
* **Qué cambiaría en el código**:
  * **Validación matemática del OCR**: Antes de enviar la matriz al solver de Backtracking, añadir una función que verifique la coherencia del tablero (que no haya números repetidos en la misma fila, columna o cuadrante de 3x3). Si el OCR comete un error e introduce un número ilegal, el solver colapsará intentando resolver un sudoku imposible.
  * **Estabilización temporal**: Crear un acumulador de frames (un buffer) que almacene las lecturas del OCR durante 10 frames consecutivos. Solo se ejecuta el solver si las lecturas se mantienen estables, evitando parpadeos de números erróneos.
* **Qué añadiría en la memoria**:
  * **Discusión técnica sobre Tesseract**: Explicar por qué Tesseract falla con dígitos individuales en celdas pequeñas y detallar el preprocesamiento morfológico aplicado (erosión/dilatación para limpiar ruido de tinta, reescalado bilineal y agregado de bordes blancos artificiales).
* **Qué falta**: Cambiar la lectura de Tesseract (que es lenta y requiere dependencias del sistema operativo) por un clasificador CNN muy ligero en PyTorch/OpenCV entrenado con el dataset MNIST para clasificar dígitos del 1 al 9 a gran velocidad.

### Opcional 5: Sustitución de DNI
* **Estado actual**: Captura de plantilla SIFT, marcado interactivo del ROI de la foto, estimación RANSAC, homografía y renderizado con alpha blending.
* **Qué cambiaría en el código**:
  * **Seguimiento híbrido (SIFT + Optical Flow)**: SIFT es costoso para ejecutar en cada frame (provoca caídas de FPS). Cambiar el diseño para que, una vez que SIFT calcula la homografía inicial, los puntos de la tarjeta se sigan mediante Flujo Óptico (KLT tracker). Solo se vuelve a lanzar SIFT si se pierde el tracking.
* **Qué añadiría en la memoria**:
  * **Mitigación de brillos**: Explicar cómo afectan los reflejos especulares de las fundas de plástico del DNI a los descriptores locales SIFT y proponer soluciones como el filtrado de saturación de color o la ecualización adaptativa de histogramas (CLAHE).
* **Qué falta**: Un mecanismo que detecte cuándo el DNI está demasiado inclinado o muy lejos de la cámara y oculte/difumine la imagen sustituida para evitar deformaciones proyectivas aberrantes.

### Opcional 6: Mosaico Panorámico
* **Estado actual**: Grafo de emparejamientos SIFT, encadenamiento BFS de homografías, composición y comparación con `cv.Stitcher`.
* **Qué cambiaría en el código**:
  * **Mezcla lineal de costuras (Feathering)**: En lugar de un solapamiento directo, aplicar una máscara de degradado lineal (rampa de pesos de 1 a 0) en las zonas de superposición de las imágenes para suavizar la transición visual y eliminar las costuras duras.
* **Qué añadiría en la memoria**:
  * **Ecuaciones de propagación de matrices**: Detallar el desarrollo matemático de cómo se multiplican las homografías sucesivas en cascada a través de las ramas del grafo resuelto con BFS ($H_{global} = H_{padre} \cdot H_{actual}$).
  * **El problema de la acumulación de error (Drift)**: Explicar por qué al unir más de 4 o 5 imágenes seguidas, los pequeños errores de estimación de homografías se van sumando, distorsionando las últimas fotos de la cadena, y cómo OpenCV soluciona esto mediante una optimización global de haces (*Bundle Adjustment*).
* **Qué falta**: El cálculo automático del tamaño óptimo de la imagen de destino analizando los extremos proyectados de todas las fotos, evitando recortar los márgenes de forma rígida.

### Opcional 7: Realidad Aumentada (Objetos con Ratón)
* **Estado actual**: Detección de tablero, homografía inversa para registrar clics, estimación PnP para coordenadas 3D, y dibujo de cubos proyectados con transparencias.
* **Qué cambiaría en el código**:
  * **Añadir sombras proyectadas**: Para dar un aspecto fotorrealista premium, proyectar una máscara de sombra poligonal oscura con transparencia en el plano del suelo ($Z=0$) desplazada en dirección opuesta a un punto de luz virtual definido.
  * **Filtros de oclusión básicos**: Segmentar el color de la piel del usuario para que, si pasa la mano por encima del tablero, los cubos AR queden ocluidos por detrás en lugar de renderizarse sobre su mano.
* **Qué añadiría en la memoria**:
  * **Física y Gravedad**: Proponer matemáticamente cómo integrar un motor físico básico (usando el vector de gravedad deducido de la matriz de rotación $R$ obtenida con PnP) para que los cubos caigan o deslicen si el usuario inclina el tablero físico.
* **Qué falta**: Un menú de selección interactivo en pantalla para alternar entre diferentes formas geométricas tridimensionales (esferas, pirámides, cilindros) además del cubo por defecto.

### Opcional 8: Reconstrucción COLMAP
* **Estado actual**: Script de automatización CLI, pasos de extracción, matching, SfM (sparse cloud) y MVS (dense cloud) y visualización.
* **Qué cambiaría en el código**:
  * **Cálculo automático de máscara de fondo**: Si el objeto se fotografió rotando sobre una mesa, el fondo de la habitación confunde a COLMAP al permanecer estático mientras el objeto se mueve. Modificar el script para que ignore características del fondo mediante segmentación por color o detección de silueta.
* **Qué añadiría en la memoria**:
  * **Reconstrucción de malla superficial (Mesh)**: Describir el proceso matemático de reconstrucción de Poisson (*Poisson Surface Reconstruction*) o envolturas convexas (*Alpha Shapes*) para unir la nube de puntos densa en una superficie sólida de triángulos lista para texturizar.
  * **Alternativas Modernas**: Añadir una discusión teórica comparativa entre la fotogrametría clásica (SfM/MVS de COLMAP) y las técnicas de representación neuronal del 3D emergentes: **NeRF** (Neural Radiance Fields) y **3D Gaussian Splatting**, analizando tiempos de procesado y calidad de rendering.
* **Qué falta**: Realizar una calibración métrica del modelo resultante introduciendo una referencia física (p. ej. una regla en la escena) y escalando la nube de puntos mediante la CLI `colmap model_aligner`.