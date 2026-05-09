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
    parser.add_argument('--gpu', action='store_true', help="Usar GPU para Feature Extraction (si disponible)")
    args = parser.parse_args()

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

    use_gpu = '1' if args.gpu else '0'

    print("\n" + "="*60)
    print("PASO 1/4: Extracción de características (SIFT)")
    print("="*60)
    run_cmd([
        'colmap', 'feature_extractor',
        '--database_path', db_path,
        '--image_path', args.images,
        '--ImageReader.single_camera', '1',
        '--SiftExtraction.use_gpu', use_gpu
    ])

    print("\n" + "="*60)
    print("PASO 2/4: Matching exhaustivo entre pares de imágenes")
    print("="*60)
    run_cmd([
        'colmap', 'exhaustive_matcher',
        '--database_path', db_path,
        '--SiftMatching.use_gpu', use_gpu
    ])

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
    
    run_cmd([
        'colmap', 'patch_match_stereo',
        '--workspace_path', dense_dir,
        '--workspace_format', 'COLMAP',
        '--PatchMatchStereo.geom_consistency', 'true'
    ])
    
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
    print(f"\nPara visualizar el modelo 3D:")
    print(f"  colmap gui  (luego File > Import Model...)")
    print(f"  O con MeshLab/CloudCompare para el archivo .ply")


if __name__ == "__main__":
    main()
