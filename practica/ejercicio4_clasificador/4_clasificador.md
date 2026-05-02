# Ejercicio 4: Clasificador de Imágenes Modular

El presente ejercicio aborda la implementación de un clasificador interactivo en tiempo real que captura entradas desde la fuente de vídeo y las asocia con modelos previamente memorizados. Dada la variedad morfológica de los elementos a reconocer, se ha optado por una **arquitectura modular paralela** que permite intercambiar en caliente la métrica de similitud empleada sin afectar al ciclo general del programa.

## 1. Arquitectura del Sistema

El flujo de trabajo se encuentra dividido lógicamente en dos componentes modulares:
*   **`4_clasificador.py`**: Archivo orquestador. Inicia la captura del *video stream*, mantiene el estado de sesión y persiste la matriz de modelos, procesa la entrada de captura asíncrona (*mediante la tecla 'C'*) y maneja la visualización UI sobre el canvas evaluando de forma iterativa el menor coste de cada métrica.
*   **`metodos.py`**: Módulo dependiente que encapsula, bajo una interfaz unificada (métodos abstractos de extracción, procesado y comparación por distancias), las tres heurísticas matemáticas requeridas: Descriptores SIFT, Espacio Latente Computacional (*Embedder* generalista) y el Análisis Numérico de Procrustes para morfología dinámica de manos.

---

## 2. Métodos, Pruebas y Resultados de Rendimiento

Para demostrar la integridad algorítmica del código, se ha puesto a prueba interactiva a cada iteración para determinar los nichos de efectividad de las distintas propuestas implementadas:

### A) Heurística SIFT (Scale-Invariant Feature Transform)
El algoritmo clásico **SIFT** basa su eficiencia en la localización sistemática de altas frecuencias espaciales y texturas intensas (patrones de esquinas, logotipos o contrastes abruptos). Utiliza la denominada "Prueba de la Razón" matemática (*Ratio Test de Lowe*) para discriminar descriptores locales erróneos en el cálculo del *matching*. Como su nombre explicita, la transformación presenta robustas tolerancias a grandes cambios de escalado y rotaciones 2D a la hora de encontrar un objeto de carátula plana registrado previamente.

> **MODELO INTRODUCIDO:**
> ![Modelo SIFT](modelo_sift.jpg)
> 
> **EJECUCIÓN DEL CLASIFICADOR (Reconocimiento frente a cambios 2D):**
> ![Captura de ejecución reconociendo con SIFT](captura_sift.png)

### B) MobileNet V3 Embedder (Inferencia Semántica Convulcional)
Esta técnica delega la búsqueda clásica de características formales u orientaciones de esquina a cambio de proyectar el *frame* en un espacio de características latentes (embedding de punto flotante) extraído mediante una red neuronal profunda pre-entrenada, evaluándose probabilísticamente usando mediciones afines a la Similitud del Coseno. La red comprende heurísticamente el concepto físico frente a la forma geométrica, dotándola de excelentes virtudes probabilísticas de categorizar un subgénero general (p.ej.: "esto tiene semejanza estructural de taza frente a un teclado").

**Limitación técnica principal:**
Se ha evidenciado una limitación severa del `Embedder` a nivel de usabilidad básica respecto a la posición (invariancias de traslación global). El *Embedder* evalúa estáticamente el mapa estructural de la escena completa a la par; si el objeto modelado como origen sufre un desplazamiento posicional importante alterando significativamente el *background*, sus mapas de características reaccionan devolviendo vectores altamente diferenciados causando rechazos.
*Estrategia de compensación:* En entornos finales este tipo de modelos embebidos convive necesariamente con etapas previas de segmentación algorítmica; para mitigar dicha limitante el código actual demandaría de la injerencia inter-bloque de localizadores *ROIs* (como los experimentados en la práctica de "Background Substraction" MOG2) o arquitecturas YOLO para generar un *bounding-box* (*Crop*) que destile únicamente los tensores del propio objeto central evadiendo el marco general.

> **MODELO INTRODUCIDO:**
> ![Modelo objeto artificial](modelo_objeto.jpg)
> 
> **EJECUCIÓN DEL CLASIFICADOR (Reconocimiento del objeto 3D genérico):**
> ![Captura de ejecución reconociendo objeto](captura_objeto.png)

### C) Gestos Morfológicos de Manos (Alineamiento de Procrustes sobre Inferencias Landmarker)
Usando los rastreadores osteomiméticos de librerías avanzadas (*MediaPipe Hands*), recabamos una representación escalar puramente geométrica del esqueleto del usuario (conjunto discreto de hitos espaciales ($X,Y,Z$) de sus falanges).

Debido a que MediaPipe no normaliza temporalidades orgánicas (cercanía a ópticas, posicionamiento a la redonda frente a la cámara web o cabeceos de la postura de la muñeca del usuario), se le ha inyectado satisfactoriamente un proceso explícito para resolver el **Problema Ortogonal de Procrustes**: 

De esta forma, cuando se recibe una disposición $N \times 3$, el sistema actualiza eficientemente la disposición mediante operaciones matriciales: transladando ambas nubes de puntos de forma geocéntrica (vía deducción elemental), atenuando escalaridad a factor neutro limitándose a la Norma Unitaria de Frobenius, y resolviendo analíticamente el ajuste ideal de giro calculando la covarianza de ambas matrices cruzadas aplicando el **Análisis de Descomposición Espacial SVD**. Esta ampliación le confiere a los gestos evaluados invencibilidad posicional.

> **MODELO DE GESTO INTRODUCIDO:**
> ![Modelo del esqueleto de mano introducido](modelo_mano.jpg)
> 
> **EJECUCIÓN DEL CLASIFICADOR (Alineamiento Ortogonal de la Mano evaluada):**
> ![Captura de reconocimiento de mano SVD](captura_mano.png)
