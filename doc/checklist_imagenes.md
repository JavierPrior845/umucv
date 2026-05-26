# Checklist de Entregables Visuales y Directorios
Esta guía sirve como hoja de ruta para completar todas las imágenes, vídeos y carpetas de datos auxiliares que el archivo \`doc.tex\` espera encontrar a la hora de compilar el documento PDF final. 

Asegúrate de respetar las rutas y los nombres de archivo indicados (o, en su defecto, actualiza el archivo \`.tex\` si decides cambiarlos).

---

## Ejercicios Obligatorios

### Ejercicio 1: Calibración
- [ ] **Imagen de demostración**: \`imagenes/ejercicio1/grid.png\`
  - *Qué es*: Captura de pantalla ejecutando \`ejercicio1_grid.py\`, donde se vea la línea base roja y la cuadrícula verde proyectadas geométricamente sobre la habitación.
- [ ] **Directorio requerido**: \`practica/ejercicio1_calibracion/fotos_calibracion/\`
  - *Qué es*: Carpeta con la batería de fotos del tablero de ajedrez (chessboards) capturadas desde distintos ángulos para generar \`calib.txt\`.

### Ejercicio 2: Análisis de Tráfico
- [ ] **Imagen de tracking**: \`imagenes/ejercicio2/captura_ventanas.png\`
  - *Qué es*: Captura mostrando simultáneamente la ventana "Trafico" (bounding boxes) y la ventana "Mascara" (visión en blanco y negro de los coches).
- [ ] **Imagen del histograma**: \`imagenes/ejercicio2/grafica_trafico.png\`
  - *Qué es*: El archivo generado automáticamente por el propio script al pulsar la tecla \`q\`.

### Ejercicio 3: Videovigilancia (Actividad)
- [ ] **Imagen de detección**: \`imagenes/ejercicio3/captura_vigilancia.png\`
  - *Qué es*: Captura de la ventana principal donde se aprecie a una persona detectada (bounding box "person") y con la zona de su cuerpo distorsionada por el efecto de difuminado/pixelado.
- [ ] **Captura del móvil**: \`imagenes/ejercicio3/captura_telegram.png\`
  - *Qué es*: Captura de pantalla de la app de Telegram donde se demuestre la llegada del mensaje automatizado "Evento detectado..." junto con la foto.

### Ejercicio 4: Clasificador Modular
El documento LaTeX está estructurado para enseñar un modelo original y una prueba en vivo por cada heurística.
- **SIFT (Texturas):**
  - [ ] \`imagenes/ejercicio4/sift/modelo_0.png\` (Foto cruda guardada del Objeto 1, ej. Videojuego).
  - [ ] \`imagenes/ejercicio4/sift/modelo_0_captura.png\` (Captura reconociéndolo girado).
  - [ ] \`imagenes/ejercicio4/sift/modelo_1.png\` (Foto cruda del Objeto 2, ej. Libro).
  - [ ] \`imagenes/ejercicio4/sift/modelo_1_captura.png\` (Captura reconociéndolo ampliado).
  - [ ] \`imagenes/ejercicio4/sift/no_modelo.png\` (Captura fallando intencionadamente con un objeto desconocido).
- **Embedder (Objetos 3D):**
  - [ ] \`imagenes/ejercicio4/embedder/modelo_0.png\` (Foto del objeto).
  - [ ] \`imagenes/ejercicio4/embedder/modelo_0_captura.png\` (Reconociendo el objeto).
- **Procrustes SVD (Manos):**
  - [ ] \`imagenes/ejercicio4/manos/modelo_1.png\` & \`modelo_1_captura.png\` (Gesto de Victoria).
  - [ ] \`imagenes/ejercicio4/manos/modelo_2.png\` & \`modelo_2_captura.png\` (Gesto OK).
- [ ] **Vídeo (Opcional)**: \`ejercicio4_clasificador/ejemplo_ejecucion_manos.mkv\` (Un pequeño clip usando las manos).
- [ ] **Directorios requeridos**: Las carpetas donde has estado guardando tus modelos mediante el script (por ejemplo \`practica/ejercicio4_clasificador/modelos_sift/\`, \`modelos_ia/\`...).

### Ejercicio 5: Deep Learning (YOLO)
- [ ] **Directorio requerido**: La carpeta íntegra del Dataset utilizado para entrenar. Debe contener la subcarpeta de imágenes y la de \`labels\` (los \`.txt\` con las cajas de anotación).
- *Nota*: La documentación no exige imagen explícita para el PDF (se vale del texto del terminal), pero siempre es recomendable adjuntar el archivo \`best.pt\` y un video corto inferiendo.

### Ejercicio 6: Rectificación y Medición
- [ ] **Imagen de calibración**: `imagenes/ejercicio6/calibracion.png`
  - *Qué es*: Foto capturada usando `stream.py` que se tomó como base para calcular la homografía.
- [ ] **Imagen de validación del carnet**: `imagenes/ejercicio6/mediciones_carnet.png`
  - *Qué es*: Captura o montaje doble mostrando la comprobación de que el ancho (5.4 cm) y el largo (8.5 cm) se miden correctamente en el propio carnet de conducir.
- [ ] **Imagen de medición del metro**: `imagenes/ejercicio6/medicion_metro.png`
  - *Qué es*: Captura midiendo la cinta métrica colocada plana sobre la mesa para corroborar el correcto funcionamiento de la homografía en diferentes distancias del plano.
- [ ] **Imagen de detalle del metro**: `imagenes/ejercicio6/metro_detalle.png`
  - *Qué es*: Foto de primer plano del metro para poder contrastar y leer visualmente los números reales en la entrega.
- [X] **Recursos adicionales requeridos (no van en la documentación)**:
  - [X] El script auxiliar de selección: `practica/ejercicio6_rectificacion/obtener_pixeles.py`
  - [X] El archivo de referencias de tu tarjeta: `practica/ejercicio6_rectificacion/referencias.txt`
  - [X] La foto original de prueba: `practica/ejercicio6_rectificacion/20260521-194404.png` (o similar)
  - [X] **Vídeo de demostración (Recomendado)**: `practica/ejercicio6_rectificacion/demostracion_medicion.mp4` (o `.mkv`), mostrando el uso interactivo de la herramienta en tiempo real sobre la mesa.
  
---

## Ejercicios Opcionales

### Opcional 1: Implementación propia de Algoritmo (Sobel)
- [X] **Imagen comparativa**: \`imagenes/opcionales/captura_sobel.png\`
  - *Qué es*: Captura de pantalla de la ventana dividida que muestra el proceso Numpy a la izquierda y el proceso nativo de OpenCV a la derecha con sus FPS estables.

### Opcional 2: Controlador Sin Contacto (Manos)
- [X] **Imagen de control**: \`imagenes/opcionales/captura_controlador.png\`
  - *Qué es*: Captura de la ejecución donde tu mano está girada o acercada, demostrando que el polígono virtual (cuadrado) ha reaccionado haciendo rotación y zoom correspondientemente (visible en el texto verde superior).

### Opcional 3: Ego-Motion (Lucas-Kanade)
- [X] **Imagen de flujo**: \`imagenes/opcionales/captura_egomotion.png\`
  - *Qué es*: Captura mientras rotas la cámara hacia un lado. Deben verse las líneas de rastreo de colores, y el texto indicando la dirección predominante (ej. "LEFT") junto con la velocidad angular en grados.

### Opcional 4: Sudoku AR
- [X] **Imagen de resolución AR**: `imagenes/opcionales/captura_sudoku.png`
  - *Qué es*: La captura de pantalla que demuestra cómo el programa ha detectado el Sudoku y le está dibujando los números verdes por encima en tiempo real. ¡Justo la imagen que acabas de enseñarme!

### Opcional 5: Sustitución de Foto de DNI
- [X] **Imagen del cambiazo**: `imagenes/opcionales/captura_dni.png`
  - *Qué es*: Ejecuta el script pasándole una foto de broma. Haz la captura de pantalla cuando la cámara enfoque a un carnet real físico y la cara falsa aparezca deformada superponiéndose a la tarjeta real de forma creíble.

### Opcional 6: Mosaico Panorámico
- [X] **Imágenes finales**: `../practica/opcionales/panorama_manual.jpg` y `panorama_opencv.jpg`
  - *Qué es*: Se hace referencia directamente a las dos imágenes resultado arrojadas por tu script en la carpeta de la práctica. Ya están referenciadas en el LaTeX.
- [X] **Directorio requerido**: Carpeta contenedora de las fotografías origen sin procesar (ej. `practica/opcionales/fotos_panorama/`).

### Opcional 7: Realidad Aumentada (Objetos Virtuales con el Ratón)
- [X] **Imagen de demostración**: `imagenes/opcionales/captura_objetos_ar.png` (Estructura LaTeX y directorio creados. Pendiente de guardar captura de pantalla durante la ejecución física).

### Opcional 8: Reconstrucción 3D con COLMAP
- [x] **Imagen de la reconstrucción**: `doc/imagenes/opcionales/captura_colmap_gui.png`
  - *Qué es*: Captura de pantalla de la interfaz gráfica de COLMAP (`colmap gui`) importando el modelo disperso (`sparse/0`), mostrando la nube de puntos del zapato y los conos de las cámaras calibradas flotando en el espacio 3D.
- [x] **Entregables de código y datos requeridos**:
  - El script orquestador: `practica/opcionales/opc8_colmap.py`
  - La carpeta con tus fotos: `practica/opcionales/fotos_colmap/`
  - La carpeta con los binarios del modelo disperso: `practica/opcionales/modelo3d_colmap/colmap_model/sparse/0/` (contiene `cameras.bin`, `images.bin` y `points3D.bin`).
