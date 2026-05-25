#!/usr/bin/env python

# Opcional 8: Reconstrucción 3D con COLMAP
# Este script es un helper que automatiza las llamadas a COLMAP por línea de comandos
# para realizar una reconstrucción SfM (Structure from Motion) de un objeto a partir
# de imágenes/fotos tomadas desde diferentes ángulos.
#
# Prerrequisito: COLMAP instalado en el sistema.
# sudo apt install colmap  (Ubuntu/Debian)
# o descargable de: https://colmap.github.io/

import os
import subprocess
import argparse
import sys

def run_cmd(cmd, check=True):
    """Ejecuta un comando de shell mostrando la salida."""
    print(f"\n>>> {' '.join(cmd)}\n")
    result = subprocess.run(cmd, capture_output=False, text=True)
    if check and result.returncode != 0:
        print(f"ERROR: El comando falló con código {result.returncode}")
        sys.exit(1)
    return result

def verificar_colmap():
    """Comprueba que COLMAP esté instalado."""
    result = subprocess.run(['colmap', '--help'], capture_output=True, text=True)
    if result.returncode not in [0, 1]:  # colmap --help puede devolver 1 y es ok
        if 'colmap' not in result.stderr.lower() and 'colmap' not in result.stdout.lower():
            print("ERROR: COLMAP no está instalado o no está en el PATH.")
            print("Instálalo con: sudo apt install colmap")
            print("O visita: https://colmap.github.io/")
            return False
    print("COLMAP detectado correctamente.")
    return True


def check_gpu():
    """Comprueba si el sistema tiene una GPU NVIDIA disponible y configurada."""
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Reconstrucción 3D automática con COLMAP (SfM)",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Ejemplo de uso:
  python opc8_colmap.py --images mis_fotos/ --output reconstruccion_3d/
  
Después podrás ver el modelo abriendo el GUI de COLMAP:
  colmap gui
  Abrir proyecto en: reconstruccion_3d/
        """
    )
    parser.add_argument('--images', required=True, help="Carpeta con las imágenes del objeto")
    parser.add_argument('--output', required=True, help="Directorio donde guardar los resultados")
    parser.add_argument('--gpu', action='store_true', help="Forzar el uso de GPU para Feature Extraction")
    args = parser.parse_args()

    # Detectar si estamos en Google Colab
    is_colab = 'google.colab' in sys.modules
    if is_colab:
        print("\n>>> [INFO] Detectado entorno Google Colab. Optimizando configuraciones...")

    # Verificar COLMAP
    if not verificar_colmap():
        sys.exit(1)
    
    # Verificar directorio de imágenes
    if not os.path.isdir(args.images):
        print(f"ERROR: El directorio de imágenes no existe: {args.images}")
        sys.exit(1)
    
    n_imgs = len([f for f in os.listdir(args.images) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    if n_imgs < 3:
        print(f"ERROR: Se necesitan al menos 3 imágenes. Encontradas: {n_imgs}")
        sys.exit(1)
    
    print(f"Imágenes encontradas: {n_imgs}")
    
    # Crear estructura de directorios de COLMAP
    db_path = os.path.join(args.output, "database.db")
    sparse_dir = os.path.join(args.output, "sparse")
    dense_dir = os.path.join(args.output, "dense")
    os.makedirs(sparse_dir, exist_ok=True)
    os.makedirs(dense_dir, exist_ok=True)

    # Decidir uso de GPU
    gpu_available = check_gpu()
    # Si estamos en Colab y hay GPU, o si el usuario lo pide y hay GPU, la usamos
    use_gpu_flag = args.gpu or (is_colab and gpu_available)
    if use_gpu_flag and not gpu_available:
        print("\n>>> [WARNING] Se solicitó GPU pero no se detecta hardware NVIDIA (nvidia-smi). Se usará CPU.")
        use_gpu_flag = False

    use_gpu = '1' if use_gpu_flag else '0'
    print(f"Configuración de aceleración: {'GPU NVIDIA' if use_gpu_flag else 'CPU (Sin aceleración)'}")

    print("\n" + "="*60)
    print("PASO 1/4: Extracción de características (SIFT)")
    print("="*60)
    cmd_extractor = [
        'colmap', 'feature_extractor',
        '--database_path', db_path,
        '--image_path', args.images,
        '--ImageReader.single_camera', '1',
        '--SiftExtraction.use_gpu', use_gpu
    ]
    res = subprocess.run(cmd_extractor, capture_output=False, text=True)
    if res.returncode != 0:
        if use_gpu_flag:
            print("\n>>> [WARNING] Falló la extracción con GPU (posiblemente COLMAP compilado sin soporte CUDA).")
            print(">>> Reintentando automáticamente con CPU...")
            cmd_extractor[-1] = '0'
            run_cmd(cmd_extractor)
        else:
            print(f"ERROR: El comando de extracción falló con código {res.returncode}")
            sys.exit(1)

    print("\n" + "="*60)
    print("PASO 2/4: Matching exhaustivo entre pares de imágenes")
    print("="*60)
    cmd_matcher = [
        'colmap', 'exhaustive_matcher',
        '--database_path', db_path,
        '--SiftMatching.use_gpu', use_gpu
    ]
    res = subprocess.run(cmd_matcher, capture_output=False, text=True)
    if res.returncode != 0:
        if use_gpu_flag:
            print("\n>>> [WARNING] Falló el matching con GPU (posiblemente COLMAP compilado sin soporte CUDA).")
            print(">>> Reintentando automáticamente con CPU...")
            cmd_matcher[-1] = '0'
            run_cmd(cmd_matcher)
        else:
            print(f"ERROR: El matching falló con código {res.returncode}")
            sys.exit(1)

    print("\n" + "="*60)
    print("PASO 3/4: Reconstrucción Structure from Motion (SfM)")
    print("="*60)
    run_cmd([
        'colmap', 'mapper',
        '--database_path', db_path,
        '--image_path', args.images,
        '--output_path', sparse_dir
    ])

    # Verificar resultado
    if not os.listdir(sparse_dir):
        print("No se produjo ninguna reconstrucción. Las imágenes quizás no solapan suficientemente.")
        sys.exit(1)

    print("\n" + "="*60)
    print("PASO 4/4: Densificación de la nube de puntos (MVS)")
    print("="*60)
    
    # Encontrar el subdirectorio con la reconstrucción (suele ser '0')
    recon_dirs = sorted(os.listdir(sparse_dir))
    sparse_input = os.path.join(sparse_dir, recon_dirs[0])
    
    run_cmd([
        'colmap', 'image_undistorter',
        '--image_path', args.images,
        '--input_path', sparse_input,
        '--output_path', dense_dir,
        '--output_type', 'COLMAP'
    ])
    
    # Intentar patch_match_stereo
    # Este comando requiere GPU CUDA de forma obligatoria.
    # Si falla, capturamos el error para no abortar el script y permitir usar la nube dispersa (SfM).
    print("\nIntentando densificación (MVS)...")
    res_pm = subprocess.run([
        'colmap', 'patch_match_stereo',
        '--workspace_path', dense_dir,
        '--workspace_format', 'COLMAP',
        '--PatchMatchStereo.geom_consistency', 'true'
    ], capture_output=True, text=True)
    
    if res_pm.returncode != 0:
        print("\n" + "="*60)
        print("AVISO: La densificación (MVS) requiere CUDA y no está disponible en este equipo.")
        print("Sin embargo, la reconstrucción dispersa (SfM) se completó con éxito.")
        print("="*60)
        print(f"\nResultados guardados en: {args.output}")
        print(f"  - Nube de puntos dispersa (SfM): {sparse_input}")
        print("\nPara visualizar la nube de puntos dispersa en 3D:")
        print("  1. Ejecuta en el terminal: colmap gui")
        print("  2. En el menú superior, ve a: File > Import model")
        print(f"  3. Selecciona la carpeta: {sparse_input}")
        sys.exit(0)
    
    run_cmd([
        'colmap', 'stereo_fusion',
        '--workspace_path', dense_dir,
        '--workspace_format', 'COLMAP',
        '--input_type', 'geometric',
        '--output_path', os.path.join(dense_dir, 'fused.ply')
    ])

    print("\n" + "="*60)
    print("¡RECONSTRUCCIÓN COMPLETADA!")
    print("="*60)
    print(f"\nResultados guardados en: {args.output}")
    print(f"  - Nube de puntos dispersa (SfM): {sparse_dir}/")
    print(f"  - Nube de puntos densa (MVS):    {dense_dir}/fused.ply")
    if is_colab:
        print("\n>>> [CONSEJO COLAB] Ya puedes descargar el archivo 'fused.ply' de la barra lateral izquierda.")
    else:
        print(f"\nPara visualizar el modelo 3D:")
        print(f"  colmap gui  (luego File > Import Model...)")
        print(f"  O con MeshLab/CloudCompare para el archivo .ply")


if __name__ == "__main__":
    main()
