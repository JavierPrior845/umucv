# Ejercicio 2: Análisis de Tráfico

En este directorio se ha resuelto el ejercicio de análisis y conteo del flujo de vehículos de una fuente de vídeo.

## Archivo principal
El script desarrollado es `2_trafico.py`. Dado que la asignatura cuenta con librerías ya integradas, podemos usar la función `autoStream` que es capaz de procesar la entrada `--dev carretera` descifrando la URL mjpg directamente desde el fichero `alias.txt` del respositorio de origen.

Para ejecutarlo:
```bash
python 2_trafico.py --dev carretera
```

## Pasos y Técnica Computacional empleada

Siguiendo las instrucciones, se han utilizado técnicas clásicas de visión por computador (sin IA/Deep Learning) apoyadas en el Background Subtractor de OpenCV:

1. **Substracción de Fondo (Background Subtraction MOG2)**: Nos permite aislar a los vehículos del fondo estático de la carretera. La imagen resultante cuenta con manchas blancas sobre un fondo negro donde detecta movimiento.
2. **Operaciones Morfológicas**: Para evitar que un camión se detecte como 3 partes distintas, o que exista ruido por vibraciones de cámara, la máscara binaria se procesa mediante una **Erosión** (para eliminar ruido de pocos píxeles) seguida de una **Dilatación** (para compactar los objetos blancos grandes que formarán el coche).
3. **Contornos y Filtrado**: Se encuentran los blobs de los coches (`cv.findContours`) y se descartan los que sean demasiado pequeños usando su área (filtro para evitar ruidos parásitos o pájaros/insectos).
4. **Seguimiento Temporal y Conteo (Tracking Básico)**:
   - Se dibuja una "Línea de Interés" virtual en pantalla a la altura $Y = 250$.
   - Se guarda el centroide ($(X, Y)$) de los vehículos de un frame, y en el siguiente se comparan con los nuevos buscando los más cercanos por distancia Euclídea. Esto permite rastrearlos y otorgarles un identificador persistente.
   - Si un vehículo pasa la Línea $Y=250$ desde arriba hacia abajo, sumamos 1 a la `Bajada`. Si lo hace de abajo a arriba, sumamos 1 a la `Subida`.
   - Se guarda un historial del instante del cruce (su temporalidad) en una lista.
5. **Generación de Gráficas Puntuales**: Al cerrar la ventana (tecla `ESC` o `q`), el script genera de forma dinámica un **histograma interactivo usando Matplotlib** que muestra el tráfico de los vehículos por tramos u horas puntas a lo largo de los segundos en los que ha funcionado el conteo.
   - Las bajadas se muestran en rojo y las subidas en verde.
   - La foto se guarda automáticamente como `grafica_trafico.png`.
