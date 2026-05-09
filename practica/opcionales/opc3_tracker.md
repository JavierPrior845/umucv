# Opcional 3: Estimación de Ego-Motion y Velocidad Angular con Lucas-Kanade

Este ejercicio extiende el script básico de seguimiento de esquinas `lk_track.py` para deducir no solo cómo se mueven los objetos en el vídeo, sino **cómo se está moviendo la propia cámara** en el mundo 3D (Ego-Motion).

## Estrategia de Implementación

Hemos añadido dos algoritmos de análisis sobre los vectores de Flujo Óptico (Optical Flow) obtenidos en cada fotograma:

### 1. Dirección del Movimiento (Pan / Tilt / Dolly)
Si asumimos que la mayoría de los puntos fuertes rastreados (`goodFeaturesToTrack`) pertenecen al fondo estático de la habitación, podemos aplicar una inversión de la relatividad clásica: el movimiento promedio de los píxeles es inverso al de la cámara.
- **Movimientos Planos (X, Y)**: Si el desplazamiento promedio de los 500 puntos rastreados es masivo hacia la Derecha ($+\Delta x$), deducimos inequívocamente que la cámara se ha desplazado/girado hacia la **Izquierda (LEFT)**. Lo mismo aplica para los ejes verticales (UP/DOWN).
- **Expansión y Contracción Radial (Z)**: Para detectar si la cámara avanza (FORWARD) o retrocede (BACKWARD), el sistema calcula el vector que va desde el centro exacto del fotograma hacia cada punto. Si aplicamos un **Producto Escalar (Dot Product)** entre el vector de movimiento y el vector radial centrífugo, podemos saber matemáticamente si los puntos se están "escapando" hacia los bordes de la imagen (lo que implica que la cámara avanza) o convergiendo hacia el centro.

### 2. Velocidad Angular (Grados por Segundo)
Una vez conocemos la velocidad en píxeles $\Delta x$ por fotograma, se calcula la velocidad en grados físicos.
- Se ha parametrizado el script con un `FOV_H` (Campo Visual Horizontal) estimado en 60 grados.
- Dividiendo 60 entre el ancho de la resolución (p.ej., 640px) obtenemos cuántos grados físicos representa el movimiento de un solo píxel.
- Multiplicando esta relación por $\Delta x$ y por los Fotogramas por Segundo actuales ($FPS$), obtenemos en tiempo real los $^\circ/s$ a los que está rotando la mano o el trípode del operador.

> **Nota para la prueba**: Es crucial usar un fondo con bastante textura en la habitación para que el rastreador consiga enganchar suficientes características para hacer el cálculo del promedio estadístico robusto.
