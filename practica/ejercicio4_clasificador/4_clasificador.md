# Ejercicio 4: Clasificador de Imágenes Modular

Este ejercicio implementa un sistema flexible de reconocimiento de imágenes que permite comparar la entrada de vídeo con una base de datos de modelos (imágenes guardadas) utilizando diferentes estrategias algorítmicas.

## Estructura del Sistema

Se ha diseñado una arquitectura modular dividida en dos archivos para facilitar la extensión con nuevos métodos:

1.  **`metodos.py`**: Contiene las clases que envuelven la lógica de cada algoritmo (SIFT, Embedder, Procrustes). Cada clase implementa una interfaz común para extraer descriptores y comparar distancias.
2.  **`4_clasificador.py`**: Script principal que gestiona la carga de modelos desde una carpeta, la interacción con el usuario (tecla 'c' para capturar nuevos modelos) y la visualización de resultados en tiempo real.

## Métodos Implementados

### 1. SIFT (Scale-Invariant Feature Transform)
Ideal para reconocer objetos planos con mucha textura y detalles (ej. portadas de juegos, carátulas de CD, cuadros).
- **Cómo funciona**: Extrae puntos clave y descriptores locales. Compara el frame actual mediante el "Ratio Test" de Lowe contra cada modelo guardado.
- **Resultado**: El modelo con más coincidencias ("matches") válidas es el ganador.

### 2. MediaPipe Embedder (Deep Learning)
Utiliza una red neuronal (MobileNet V3) para extraer un vector de características (embedding) de la imagen completa.
- **Cómo funciona**: Compara los vectores mediante la **Similitud Coseno**.
- **Ventaja**: Es capaz de reconocer objetos generales y escenas aunque cambie ligeramente el punto de vista o la iluminación, ya que entiende el "contenido" semántico.

### 3. Manos y Distancia Procrustes (Gesto de manos)
Especializado en detectar y comparar la forma de la mano.
- **Cómo funciona**:
    - Usa **MediaPipe Hands** para extraer los 21 hitos (landmarks) 3D de la mano.
    - Aplica una **normalización Procrustes simplificada**: centra el conjunto de puntos en el origen y escala su tamaño para que la norma de Frobenius sea igual a 1.
    - Compara la distancia Euclídea entre el gesto actual y los gestos guardados.
- **Uso**: Permite reconocer gestos como "OK", "Victoria", "Palma", etc.

## Instrucciones de Uso

Ejecuta el script indicando la carpeta de modelos y el método deseado:

```bash
# Para SIFT (Objetos con textura)
python 4_clasificador.py --models=modelos_sift --method=sift

# Para Embeddings (Objetos generales)
python 4_clasificador.py --models=modelos_obj --method=embedder

# Para Gestos (Manos)
python 4_clasificador.py --models=mis_gestos --method=manos
```

**Interacción**:
- Pulsa **'c'** para capturar el frame actual y guardarlo como un nuevo modelo en la carpeta indicada. Se empezará a usar inmediatamente para la clasificación.
- Pulsa **'q'** o **ESC** para salir.
