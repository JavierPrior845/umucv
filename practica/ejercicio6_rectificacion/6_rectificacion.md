# Ejercicio 6: Rectificación y Medición

Este ejercicio demuestra cómo usar **Homografías** para deshacer la deformación de perspectiva que sufren las cámaras al fotografiar planos inclinados. Esto nos permite hacer mediciones precisas en 2D (distancias, tamaños) sobre una fotografía.

## Metodología

La función matemática que relaciona los píxeles de una imagen distorsionada con sus coordenadas reales en un plano métrico se denomina **homografía** (una transformación proyectiva 2D).

### 1. El Fichero de Referencias
Para que el ordenador pueda deducir esa matriz matemática, necesita que le des al menos **4 puntos** de los que conozcas tanto sus coordenadas en la foto (`X,Y` en píxeles) como en la realidad (`X,Y` en centímetros o metros).

Ejemplo del contenido de `ejemplo_coins.txt`:
```
200 150 0 0
400 150 10 0
...
```
*(Puedes encontrar las coordenadas en píxeles abriendo tu foto en Paint u otra herramienta de edición).*

### 2. El Script de Medición (`6_rectificacion.py`)
El script toma la imagen y las referencias y realiza las siguientes acciones:
1.  **`cv.findHomography`**: Calcula la matriz $H$ de 3x3 que define la transformación.
2.  **`cv.perspectiveTransform`**: Permite al usuario hacer click en dos puntos cualesquiera del fotograma para aplicarles la matriz $H$ y trasladarlos mágicamente al "mundo real".
3.  **Distancia Euclídea**: Calcula la distancia matemática entre esos dos puntos reales y la pinta por pantalla.

---

## Instrucciones de Uso

Para probar la herramienta con el ejemplo ilustrativo incluido (las medidas son arbitrarias en este ejemplo):
```bash
python 6_rectificacion.py --image ../../images/coins.png --ref ejemplo_coins.txt
```
1. Se abrirá una ventana con la imagen (los puntos amarillos son los que definiste en el archivo `.txt`).
2. Haz **un clic** en un extremo del objeto que quieras medir.
3. Haz **otro clic** en el extremo opuesto.
4. Una línea verde aparecerá conectándolos y un texto te indicará la distancia en las mismas unidades que usaste en tu archivo de texto (por ejemplo, centímetros).

### Cómo usar tus propias fotos
Para resolver completamente el ejercicio debes probar esto con fotos sacadas por ti. Sigue este procedimiento:
1. Pon un folio, una tarjeta de crédito o dibuja un cuadrado de medidas conocidas en el suelo. 
2. Hazle una foto con tu cámara en ángulo.
3. Abre la foto en un visor para anotar en qué píxeles (X, Y) cayeron las 4 esquinas de la tarjeta.
4. Crea un nuevo archivo `mis_referencias.txt` poniendo esos 4 píxeles emparejados con `0 0`, `8.5 0`, `8.5 5.4`, `0 5.4` (medidas reales de la tarjeta).
5. Lanza el script: `python 6_rectificacion.py --image mi_foto.jpg --ref mis_referencias.txt`. ¡Ahora podrás medir cualquier otra cosa que aparezca en el suelo de tu foto!
