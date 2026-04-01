# Ejercicio 1: Calibración

A continuación, se detalla paso a paso cómo se ha resuelto el ejercicio de calibración utilizando las imágenes capturadas con tu propia cámara.

## Paso 1: Captura de Imágenes
El primer paso fue apuntar la cámara a un patrón tipo tablero de ajedrez (*chessboard*) desde múltiples distancias y ángulos para captar la deformación de la perspectiva. 
* Esto se realizó usando el script `code/stream.py`, y guardando pulsando la tecla `s`. Las imágenes se almacenaron en la carpeta `fotos_calibracion`.

## Paso 2: Calculo de la Matriz K y Calibración
Utilizando tus imágenes, hemos ejecutado el calibrador:
```bash
./code/calibrate/calibrate.py --dev glob:practica/ejercicio1_calibracion/fotos_calibracion/*.png
```
Esto calcula la matriz intrínseca $K$ de la cámara, el error de aproximación (RMS) y la distorsión, y actualiza el archivo `calib.txt`.
Para tu cámara obtuvimos los siguientes resultados reales:
* **RMS:** `0.369` (un valor cercano a 0, indicando una muy buena calibración).
* **Matriz de cámara (K):**
  ```text
  [[632.   0. 329.]
   [  0. 632. 229.]
   [  0.   0.   1.]]
  ```
  De esto extraemos que la distancia focal es $f_x = f_y \approx 632$, y el centro óptico es $(c_x, c_y) \approx (329, 229)$. Dado este centro óptico (que cae en el centro de la imagen capturada), la resolución es detectada sin que tengas que decírsela. A partir del centro, deducimos que la captura se hizo a $640 \times 480$: el centro teórico de 640 es 320 (cercano a 329) y el centro de 480 es 240 (cercano a 229).

## Paso 3: Calcular el Field of View (FOV)
El FOV se calcula trigonométricamente asumiendo el modelo pin-hole:
$$ \text{FOV} = 2 \times \arctan\left(\frac{\text{Lado}}{2f}\right) $$
Para tu cámara, utilizando la distancia focal obtenida $f = 632$ y su resolución detectada de $W=640$ y $H=480$:

* **FOV Horizontal ($FOV_x$):**
  $$ FOV_x = 2 \times \arctan\left(\frac{640}{2 \times 632}\right) = 2 \times \arctan(0.506) \approx 0.938 \text{ radianes} \approx 53.7^\circ $$

* **FOV Vertical ($FOV_y$):**
  $$ FOV_y = 2 \times \arctan\left(\frac{480}{2 \times 632}\right) = 2 \times \arctan(0.379) \approx 0.725 \text{ radianes} \approx 41.5^\circ $$

## Paso 4: Cuadrícula en un Plano (Script de Python)
He creado el fichero `ejercicio1_grid.py` en esta misma carpeta `practica`. 
Para ejecutarlo:
```bash
python ejercicio1_grid.py
```
**Explicación de este componente:**
Nos piden poder trazar una cuadrícula en un plano perpendicular a la cámara (como si fuera una pared enfrente tuyo). Para hacerlo, la cámara debe estar en horizontal a una altura de suelo $H$. Así:
1. El plano del "horizonte" coincide con el punto central vertical proyectado en la cámara ($c_y$).
2. A una distancia elegible $Z$ y dada nuestra altura elegible $H$, la "pared" choca con el suelo exactamente con el valor $y_{\text{base}} = f_y \frac{H}{Z} + c_y$.
3. Usamos barras desplazables (*sliders*) mediante la función de OpenCV `createTrackbar` para alterar en tiempo real la Distancia (Z) y la Altura (H).
4. El script carga el `calib.txt` y, si la imagen se procesa en tiempo real, proyecta sobre ella las líneas mediante `cv.line`.
