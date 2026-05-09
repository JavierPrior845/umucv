# Opcional 7: Realidad Aumentada — Objetos Virtuales con el Ratón

Este ejercicio implementa un sistema de **Realidad Aumentada básica sobre un plano físico**. El usuario hace clic con el ratón en cualquier punto de la pantalla donde aparece el tablero de ajedrez, y el programa coloca un objeto virtual en ese punto del plano real. A medida que muevas o gires el tablero frente a la cámara, los objetos siguen el movimiento "pegados" a su posición en el mundo.

## Funcionamiento

### 1. Detección del Plano de Referencia
Se usa un **tablero de ajedrez** estándar (7x5 por defecto) como marcador fiducial plano. En cada frame, `cv.findChessboardCorners` localiza sus esquinas con precisión subpixélica. A partir de las coordenadas conocidas de estas esquinas en el "mundo" (en unidades de cuadrado de tablero), se calcula mediante `cv.findHomography` la relación entre píxeles de la imagen y puntos del plano físico.

### 2. Conversión clic → Coordenadas del Mundo
Cuando el usuario hace clic en `(x_img, y_img)`, se aplica la homografía inversa (imagen → mundo) con `cv.perspectiveTransform`. El resultado es la coordenada `(x_mundo, y_mundo)` del punto físico del tablero en el que se hizo clic. Esta coordenada se guarda de forma permanente junto con el color y tamaño del objeto.

### 3. Proyección en cada Frame
En cada nuevo fotograma, la homografía mundo → imagen se recalcula (el tablero puede haberse movido). Los objetos guardados se re-proyectan a sus nuevas coordenadas en imagen usando la nueva homografía, dando la ilusión de que están "pegados" al tablero físico.

## Uso
```bash
# Necesitas un tablero de ajedrez impreso de 7x5 esquinas interiores
python opc7_ar_objetos.py

# Si tu tablero tiene otra dimensión (ej. 9x6):
python opc7_ar_objetos.py --patron 9x6
```

**Controles durante la ejecución:**
- **Click Izquierdo** sobre el tablero detectado → añade objeto virtual de colores.
- **'c'** → borra todos los objetos del mundo.
- **'q' / ESC** → salir.

> **Consejo**: La detección de tablero es más robusta con buena iluminación uniforme y el tablero impreso sobre papel mate (sin brillos).
