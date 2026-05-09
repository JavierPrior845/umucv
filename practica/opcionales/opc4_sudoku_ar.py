#!/usr/bin/env python

import cv2 as cv
import numpy as np
import pytesseract
from umucv.stream import autoStream
from umucv.util import putText

# --- SUDOKU SOLVER (BACKTRACKING) ---
def is_valid(board, row, col, num):
    for x in range(9):
        if board[row][x] == num:
            return False
    for x in range(9):
        if board[x][col] == num:
            return False
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[i + start_row][j + start_col] == num:
                return False
    return True

def solve_sudoku(board):
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                for num in range(1, 10):
                    if is_valid(board, i, j, num):
                        board[i][j] = num
                        if solve_sudoku(board):
                            return True
                        board[i][j] = 0
                return False
    return True

# --- OCR Y PROCESAMIENTO ---
def extract_digit(cell_img):
    """Limpia la celda y usa pytesseract para intentar extraer el número."""
    # Extraer bordes
    gray = cv.cvtColor(cell_img, cv.COLOR_BGR2GRAY)
    _, thresh = cv.threshold(gray, 150, 255, cv.THRESH_BINARY_INV)
    
    # Encontrar el contorno del número
    contours, _ = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    if not contours:
        return 0
        
    c = max(contours, key=cv.contourArea)
    if cv.contourArea(c) < 50:
        return 0 # Probablemente ruido o celda vacía
        
    x, y, w, h = cv.boundingRect(c)
    # Recortar el número con un poco de margen para Tesseract
    roi = thresh[max(0, y-5):y+h+5, max(0, x-5):x+w+5]
    if roi.size == 0: return 0
    
    # Tesseract requiere texto negro sobre blanco para funcionar bien
    roi_inv = cv.bitwise_not(roi)
    
    # --psm 10: tratar la imagen como un solo caracter. Whitelist: 1-9
    custom_config = r'--oem 3 --psm 10 -c tessedit_char_whitelist=123456789'
    text = pytesseract.image_to_string(roi_inv, config=custom_config)
    
    try:
        num = int(text.strip())
        if 1 <= num <= 9:
            return num
    except:
        pass
    return 0

def ordenar_puntos(pts):
    """Ordena 4 puntos en [Top-Left, Top-Right, Bottom-Right, Bottom-Left]"""
    pts = pts.reshape((4, 2))
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

print("\n--- SUDOKU AR + OCR ---")
print("1. Muestra un cuadrado con el sudoku a la cámara.")
print("2. Pulsa 'Espacio' para capturar la rejilla y empezar a resolver.")
print("3. Si el OCR falla, ajusta la iluminación.")
print("Pulsa 'q' o ESC para salir.\n")

estado = "BUSCANDO"
sudoku_board = np.zeros((9, 9), dtype=int)
sudoku_resuelto = np.zeros((9, 9), dtype=int)
esquinas_detectadas = None

for key, frame in autoStream():
    # Encontrar el cuadrado más grande en la imagen (asumiendo que es el Sudoku)
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    blur = cv.GaussianBlur(gray, (5, 5), 1)
    bordes = cv.Canny(blur, 50, 150)
    
    # Dilatar para conectar líneas
    kernel = np.ones((3, 3), np.uint8)
    bordes = cv.dilate(bordes, kernel, iterations=1)
    
    contours, _ = cv.findContours(bordes, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    
    max_area = 0
    mejor_contorno = None
    
    for c in contours:
        area = cv.contourArea(c)
        if area > 10000: # Ignorar ruido pequeño
            peri = cv.arcLength(c, True)
            aprox = cv.approxPolyDP(c, 0.02 * peri, True)
            if len(aprox) == 4 and area > max_area:
                mejor_contorno = aprox
                max_area = area

    if estado == "BUSCANDO":
        if mejor_contorno is not None:
            cv.drawContours(frame, [mejor_contorno], -1, (0, 255, 0), 3)
            putText(frame, "Sudoku Detectado. Pulsa ESPACIO para Escanear", (10, 30), color=(0, 255, 0))
            if key == ord(' '):
                estado = "ESCANEO_OCR"
                esquinas_detectadas = ordenar_puntos(mejor_contorno)
        else:
            putText(frame, "No se detecta rejilla (cuadrado)", (10, 30), color=(0, 0, 255))

    elif estado == "ESCANEO_OCR":
        # 1. Hacer Transformacion de Perspectiva (Plano 2D Top-Down de 450x450 px)
        dim = 450
        pts_dst = np.array([[0, 0], [dim-1, 0], [dim-1, dim-1], [0, dim-1]], dtype="float32")
        M = cv.getPerspectiveTransform(esquinas_detectadas, pts_dst)
        warp = cv.warpPerspective(frame, M, (dim, dim))
        
        # 2. Partir en 81 celdas y pasar OCR
        step = dim // 9
        print("Iniciando escaneo OCR. Esto puede tardar un poco...")
        sudoku_board = np.zeros((9, 9), dtype=int)
        
        for r in range(9):
            for c in range(9):
                # Extraemos cada celda quitándole 5 píxeles de margen (borde de la rejilla)
                celda = warp[r*step+5:(r+1)*step-5, c*step+5:(c+1)*step-5]
                num = extract_digit(celda)
                sudoku_board[r][c] = num
                
        print("Tablero Escaneado (Ceros = Celdas Vacias):")
        print(sudoku_board)
        
        # 3. Resolver
        sudoku_resuelto = sudoku_board.copy()
        if solve_sudoku(sudoku_resuelto):
            estado = "RESUELTO"
            print("¡Sudoku Resuelto con éxito!")
        else:
            estado = "ERROR"
            print("El OCR cometió un error insalvable o el tablero estaba mal.")

    elif estado == "RESUELTO":
        # Actualizamos la rejilla viva si se sigue viendo (para AR)
        if mejor_contorno is not None:
            esquinas = ordenar_puntos(mejor_contorno)
            
            # Generar imagen holográfica en plano 2D
            dim = 450
            holograma = np.zeros((dim, dim, 3), dtype=np.uint8)
            step = dim // 9
            
            # Pintar números
            for r in range(9):
                for c in range(9):
                    # Solo pintar los números que ha resuelto el bot, no los originales
                    if sudoku_board[r][c] == 0 and sudoku_resuelto[r][c] != 0:
                        num_txt = str(sudoku_resuelto[r][c])
                        # Poner texto verde en el centro de la celda
                        cx = c * step + int(step * 0.3)
                        cy = r * step + int(step * 0.7)
                        cv.putText(holograma, num_txt, (cx, cy), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Proyectar el holograma 2D al plano 3D de la cámara (Transformada Inversa)
            M_inv = cv.getPerspectiveTransform(pts_dst, esquinas)
            holograma_warp = cv.warpPerspective(holograma, M_inv, (frame.shape[1], frame.shape[0]))
            
            # Superponer el holograma sobre la imagen original usando una máscara
            gray_holo = cv.cvtColor(holograma_warp, cv.COLOR_BGR2GRAY)
            _, mask = cv.threshold(gray_holo, 10, 255, cv.THRESH_BINARY)
            mask_inv = cv.bitwise_not(mask)
            
            frame_bg = cv.bitwise_and(frame, frame, mask=mask_inv)
            frame = cv.add(frame_bg, holograma_warp)
            
            putText(frame, "SUDOKU RESUELTO (AR)", (10, 30), color=(0, 255, 0))
        else:
            putText(frame, "Muestra el Sudoku para proyectar", (10, 30), color=(0, 150, 255))
            
    elif estado == "ERROR":
        putText(frame, "Error de OCR. Pulsa ESPACIO para re-escanear", (10, 30), color=(0, 0, 255))
        if key == ord(' '):
            estado = "BUSCANDO"

    cv.imshow("Sudoku Realidad Aumentada", frame)

    if key == 27 or key == ord('q'):
        break

cv.destroyAllWindows()
