# Opcional 8: Reconstrucción de Modelo 3D con COLMAP

Este ejercicio utiliza **COLMAP**, una herramienta de código abierto para reconstrucción 3D automática basada en Structure from Motion (SfM) y Multi-View Stereo (MVS). A partir de fotografías normales de un objeto tomadas desde distintos ángulos, genera automáticamente una nube de puntos 3D densa.

## Prerrequisito: Instalar COLMAP

```bash
# Ubuntu / Debian
sudo apt install colmap

# Alternativa: descargar el binario precompilado de:
# https://colmap.github.io/
```

## Metodología del Pipeline

El script `opc8_colmap.py` automatiza el proceso completo en 4 pasos:

### Paso 1: Extracción de características (SIFT)
COLMAP analiza cada imagen y extrae sus puntos clave SIFT con descriptores. Todos se indexan en una base de datos SQLite (`database.db`).

### Paso 2: Matching Exhaustivo
Se comparan todos los pares de imágenes para encontrar correspondencias robustas entre los descriptores. Esto permite saber qué imágenes ven las mismas partes del objeto.

### Paso 3: Structure from Motion (SfM)
Con las correspondencias, COLMAP estima simultáneamente la **posición y orientación de cada cámara** en el espacio 3D (Bundle Adjustment) y la **posición 3D de cada punto clave** visible. El resultado es una **nube de puntos dispersa** (sparse cloud).

### Paso 4: Multi-View Stereo (MVS)
COLMAP densifica la nube de puntos comparando parches de píxeles de múltiples vistas. Produce una **nube densa** de millones de puntos guardada en formato `.ply`.

## Uso

```bash
# Pon las fotos de tu objeto en una carpeta (mínimo 10-20 fotos)
python opc8_colmap.py --images mis_fotos/ --output modelo3d/

# Con GPU NVIDIA (mucho más rápido):
python opc8_colmap.py --images mis_fotos/ --output modelo3d/ --gpu
```

## Consejos para tomar buenas fotos

- Rodea el objeto dando pasos laterales, tomando 1 foto cada 15-20 grados.
- La escena debe estar bien iluminada y el objeto debe tener textura (no objetos totalmente blancos ni brillantes).
- Mínimo 15-20 fotos; 40-60 fotos dan mejores resultados.

## Visualización del resultado

Después de ejecutar, abre los resultados con **MeshLab** o **CloudCompare**:
```bash
# Instalar MeshLab
sudo apt install meshlab
meshlab modelo3d/dense/fused.ply
```

O con la interfaz gráfica de COLMAP:
```bash
colmap gui
# File > Import Model > seleccionar carpeta modelo3d/sparse/0/
```
