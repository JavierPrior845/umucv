# Opcional 4: Sudoku con Realidad Aumentada y OCR

Este ejercicio aborda uno de los retos más integrales y complejos de Visión Artificial clásica: localizar una estructura paramétrica (un tablero de Sudoku) en vídeo continuo, leer sus dígitos mediante reconocimiento de caracteres (OCR), resolver el problema lógico mediante computación y proyectar la respuesta de forma volumétrica directamente sobre el papel ("Holograma AR").

## Requisitos del Sistema
Para que este ejercicio funcione, es imprescindible que tengas instalado Tesseract en tu sistema operativo, ya que el script utiliza `pytesseract` para leer los números impresos:
```bash
sudo apt install tesseract-ocr
pip install pytesseract
```

## Fases del Algoritmo Implementado

1. **Detección Geométrica (Contornos)**: En cada fotograma, el script aplica un filtro `GaussianBlur` seguido de un detector de bordes `Canny`. Se aíslan todos los contornos externos, y mediante `approxPolyDP` se extrae el cuadrilátero (4 vértices) con mayor área de la pantalla. Esto asegura que detectemos el marco exterior negro del Sudoku aunque la foto esté torcida.

2. **Homografía e Isometría (Top-Down)**: Aplicando `cv.getPerspectiveTransform` con los 4 vértices hallados, el script extrae el interior de ese marco y lo convierte en un cuadrado perfecto en memoria RAM (450x450 píxeles). Esta "vista de pájaro" o escaneo nos permite dividir el papel en exactamente 81 sub-imágenes (las 81 celdillas) por mera aritmética matricial (50x50px por celda).

3. **Reconocimiento Óptico de Caracteres (OCR)**: Cuando el usuario pulsa Espacio, se congela la rejilla y cada celda se envía a la red de *Tesseract OCR*. Para forzar la exactitud matemática de un modelo de texto genérico (diseñado originalmente para leer diccionarios), se le pasa el flag heurístico `--psm 10` (tratar como caracter solitario) y una Whitelist de Tesseract limitando la gramática permitida puramente a los dígitos `123456789`.

4. **Fuerza Bruta Dirigida (Backtracking Solver)**: La matriz NumPy de 9x9 resultante del paso de OCR contiene ceros para las celdas vacías y números interpretados para las llenas. El script incorpora un solucionador recursivo de Sudoku programado manualmente en Python con lógica de Backtracking y recursividad.

5. **Proyección Holográfica Mapeada en 3D (Augmented Reality)**:
   - El script genera un "holograma": una imagen digital 2D en fondo negro puro (máscara alpha 0) que contiene únicamente la fuente de texto de los números verdes calculados por la función Backtracking, situados ortogonalmente en sus respectivas celdas de 50x50 píxeles.
   - En cada frame nuevo, re-detectamos las esquinas de la hoja de papel moviéndose. El script usa `getPerspectiveTransform` para invertir el proceso homográfico y aplastar ese holograma 2D digital hasta ajustarlo isométrica y proyectivamente al ángulo exacto del papel en el mundo real en tiempo de ejecución.
   - Usando máscaras booleanas (`bitwise_and`, `bitwise_not`, `cv.add`), el holograma distorsionado se "sobreimpresiona" aditivamente por encima de los píxeles de la cámara orgánicos.
