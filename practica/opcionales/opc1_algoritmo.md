# Opcional 1: Implementación propia de un algoritmo

En este ejercicio se ha desarrollado desde cero una implementación matemática del popular filtro de detección de bordes **Sobel**.

## Diseño de la Solución
En lugar de utilizar dos bucles `for` anidados para recorrer cada píxel de la imagen multiplicando por la máscara 3x3 (lo cual en Python es extraordinariamente lento), se ha utilizado una **implementación vectorizada con Numpy**.

Extraemos "vistas" (slicing) desplazadas de la matriz de la imagen y las sumamos directamente. Esto simula a la perfección el comportamiento de una convolución espacial a bajo nivel, manteniendo el cálculo en el backend escrito en C de Numpy.

## Análisis de Rendimiento
El script `opc1_algoritmo.py` divide la pantalla en dos:
- **Izquierda**: Nuestra implementación manual en Python.
- **Derecha**: La función `cv.Sobel()` y `cv.magnitude()` de OpenCV.

### Resultados y Conclusiones
A pesar de haber vectorizado la operación en Numpy, el algoritmo nativo en OpenCV es consistentemente más rápido. Como se aprecia en la captura de resultados `captura_sobel.png`, la versión vectorizada matemática en Numpy se ejecuta a una media de **65 FPS (~11 ms)**, mientras que la solución de OpenCV triplica el rendimiento general alcanzando los **202 FPS (~5 ms)** a la misma resolución.

**¿Por qué OpenCV es más rápido?**
1. OpenCV está escrito en C/C++ y fuertemente optimizado para operaciones morfológicas, utilizando SIMD (Single Instruction Multiple Data) en el procesador.
2. La función de OpenCV no crea tantos arrays intermedios en memoria RAM como hace nuestra versión vectorizada al hacer *slicing* de las 8 matrices desplazadas.
3. OpenCV paraleliza automáticamente este tipo de cálculos sobre múltiples núcleos de la CPU.

En conclusión, aunque entender y programar la matemática de un algoritmo en Python/Numpy es fundamental a nivel académico, para sistemas en tiempo real es vital delegar la carga computacional a librerías optimizadas en C++.
