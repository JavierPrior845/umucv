# Opcional 6: Mosaico Automático con Homografías

Este ejercicio implementa un sistema de **cosido automático de imágenes** (*image stitching*) en Python, que crea un panorama o mosaico amplio a partir de un conjunto de fotografías parcialmente solapadas de una escena plana.

## Metodología

### 1. Construcción del Grafo de Solapamientos
No se asume ningún orden en las imágenes de entrada. El algoritmo compara todos los pares posibles usando **SIFT + Ratio Test de Lowe** para hallar correspondencias. Los pares con suficientes correspondencias (≥10 matches) quedan conectados en un grafo mediante sus homografías.

### 2. Cadena de Homografías (BFS)
Para referencia, se escoge la imagen central de la lista. Mediante una búsqueda en anchura (BFS) sobre el grafo, se calcula la homografía acumulada `H_global[i]` que lleva cada imagen `i` al espacio de coordenadas de la imagen de referencia. Si no todas las imágenes están conectadas, se avisa al usuario.

### 3. Proyección y Composición
Se proyectan todas las imágenes al espacio de la referencia usando `cv.warpPerspective` con `BORDER_TRANSPARENT` para que los píxeles vacíos no sobreescriban los ya colocados. El offset de traslación garantiza que todo quede en coordenadas positivas.

### 4. Comparación con cv.Stitcher
Seguidamente, el mismo conjunto de imágenes se pasa a `cv.Stitcher.create()`, el stitcher industrial de OpenCV. Se genera la imagen resultado y se comparan visualmente ambos enfoques.

## Uso
```bash
# Pon varias fotos solapadas de una escena plana en una carpeta y ejecuta:
python opc6_mosaico.py --dir mi_carpeta_de_fotos/ --out panorama.jpg
```
Se generarán dos archivos: `panorama_manual.jpg` (implementación propia) y `panorama_opencv.jpg` (cv.Stitcher).

> **Consejo**: Haz las fotos con un trípode o girando solo en torno a tu eje vertical. Mejor si la escena está plana (pared, suelo, cuadro).
