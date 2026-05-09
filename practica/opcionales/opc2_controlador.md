# Opcional 2: Controlador Sin Contacto de Varios Grados de Libertad

Este ejercicio implementa una interfaz Hombre-Máquina (HCI) para interactuar con aplicaciones de ordenador sin necesidad de ratón o teclado, usando únicamente una webcam y la mano.

## Funcionamiento Técnico

He utilizado el modelo pre-entrenado de **MediaPipe Hands** debido a su increíble robustez y bajo peso computacional para CPU. El programa extrae los 21 "landmarks" o puntos clave de la mano.

### Cálculo de Grados de Libertad (DoF)

Se han extraído **dos dimensiones continuas** de control a partir de la geometría de la mano en tiempo real:

1. **Ángulo de Orientación (Rotación)**:
   - Se obtiene trazando un vector direccional 2D desde la muñeca (landmark 0) hasta la punta del dedo corazón (landmark 12).
   - Aplicamos la función matemática arcotangente (`math.atan2(y, x)`) para deducir el ángulo de giro de la mano respecto a la vertical absoluta de la pantalla.

2. **Distancia a la cámara (Profundidad / Zoom)**:
   - Extraer la profundidad 'Z' real con una cámara normal 2D es complejo. Como solución elegante, mido la distancia euclídea bidimensional (en píxeles) entre el nudillo del dedo índice y el nudillo del dedo meñique.
   - Puesto que los huesos de la palma no pueden hacerse más grandes o más pequeños mágicamente en la realidad, cualquier aumento en la distancia en píxeles indica inequívocamente que la mano se está acercando a la cámara, y viceversa.
   - Esa distancia se escala linealmente para controlar el tamaño de un objeto.

### Aplicación
El script de prueba renderiza un cuadrado virtual en el centro de la pantalla. El usuario usa su mano como "volante y palanca": si acerca la mano a la pantalla el cuadrado hace "Zoom in", y si tuerce la muñeca el cuadrado rota en sincronía.
