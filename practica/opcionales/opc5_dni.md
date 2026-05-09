# Opcional 5: Sustitución de Foto del DNI en Tiempo Real (AR)

Este ejercicio implementa un efecto de **Realidad Aumentada** que detecta un DNI o tarjeta de identificación en la imagen de la cámara y sustituye dinámicamente la fotografía del portador por otra imagen, siguiendo el movimiento y la perspectiva de la tarjeta en tiempo real.

## Funcionamiento

### Fase 1 — Captura de Referencia
El usuario pulsa `'c'` cuando el DNI está bien visible y centrado. En ese momento, el script extrae sus **Puntos Clave SIFT** (descriptores invariantes a escala y rotación) de toda la tarjeta. Esta imagen queda como el "modelo" que el sistema buscará en los frames sucesivos.

### Fase 2 — Marcado del ROI
Sobre la imagen congelada, el usuario **arrastra un rectángulo con el ratón** encima de la zona de la fotografía del DNI. Esto define las 4 esquinas de la región de interés (ROI) en coordenadas del frame de referencia.

### Fase 3 — Seguimiento y Sustitución (SIFT + Homografía)
En cada frame del vídeo en directo:
1. **SIFT** extrae los descriptores del frame actual y los compara con los del frame de referencia.
2. Se aplica el **Ratio Test de Lowe** (umbral 0.75) para conservar solo las correspondencias robustas.
3. Con ≥15 matches válidos, `cv.findHomography` con **RANSAC** calcula la matriz H que describe la deformación proyectiva del DNI entre la referencia y el frame actual.
4. Las 4 esquinas del ROI se transforman con H al espacio del frame actual: `cv.perspectiveTransform`.
5. La imagen de sustitución se deforma con `cv.getPerspectiveTransform` + `cv.warpPerspective` para ajustarse al cuadrilátero resultante.
6. Se aplica **alpha blending** con una máscara suavizada para integrar la imagen sustituida de forma natural.

## Uso

```bash
# Con tu propia imagen de sustitución:
python opc5_dni.py --swap mi_foto.jpg

# Sin imagen (usa un rectángulo verde de demo):
python opc5_dni.py
```

### Controles
| Tecla | Acción |
|---|---|
| `c` | Capturar frame de referencia |
| Ratón (arrastrar) | Marcar la zona de la foto del DNI |
| `ENTER` | Confirmar ROI y activar sustitución |
| `r` | Reiniciar desde el principio |
| `q` / `ESC` | Salir |

## Consejos para mejores resultados
- El DNI debe tener **mucha textura visual** (texto, números, banderas) para que SIFT encuentre muchos puntos. La zona de la foto tiene poca textura, por eso el sistema analiza **todo el DNI** para el seguimiento.
- Una iluminación uniforme sin reflejos especulares mejora mucho la robustez del tracking.
- Ajusta la velocidad de movimiento: si mueves el DNI muy rápido, el sistema puede perder el tracking momentáneamente.
