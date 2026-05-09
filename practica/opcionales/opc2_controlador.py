#!/usr/bin/env python

import cv2 as cv
import numpy as np
import mediapipe as mp
import math
from umucv.stream import autoStream
from umucv.util import putText

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

def calcular_angulo(p1, p2):
    """Calcula el ángulo en grados entre dos puntos 2D."""
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    # math.atan2 devuelve de -pi a pi. Lo convertimos a grados.
    angulo = math.degrees(math.atan2(dy, dx))
    return angulo

def calcular_distancia(p1, p2):
    """Calcula la distancia euclídea entre dos puntos 2D."""
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

print("\n--- CONTROLADOR SIN CONTACTO ---")
print("Pon la mano frente a la cámara.")
print("- DISTANCIA: Acerca o aleja la mano para hacer más grande/pequeño el cubo.")
print("- ROTACIÓN: Gira la mano como un volante para rotar el cubo.")
print("Pulsa 'q' o ESC para salir.\n")

with mp_hands.Hands(
        model_complexity=0,
        max_num_hands=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:

    for key, frame in autoStream():
        # Voltear la imagen como un espejo para que sea intuitivo
        frame = cv.flip(frame, 1)
        h, w = frame.shape[:2]

        image_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        results = hands.process(image_rgb)

        # Variables del objeto virtual
        escala_virtual = 100
        angulo_virtual = 0
        detectado = False

        if results.multi_hand_landmarks:
            detectado = True
            hand_landmarks = results.multi_hand_landmarks[0]
            
            # Dibujar esqueleto de la mano (opcional, ayuda al feedback visual)
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Extraer coordenadas de la muñeca (0) y dedo corazón (12)
            wrist = hand_landmarks.landmark[0]
            middle_tip = hand_landmarks.landmark[12]
            
            p_wrist = (int(wrist.x * w), int(wrist.y * h))
            p_middle = (int(middle_tip.x * w), int(middle_tip.y * h))

            # Extraer coordenadas base de los dedos para estimar tamaño de la palma
            index_mcp = hand_landmarks.landmark[5]
            pinky_mcp = hand_landmarks.landmark[17]
            p_index = (int(index_mcp.x * w), int(index_mcp.y * h))
            p_pinky = (int(pinky_mcp.x * w), int(pinky_mcp.y * h))

            # 1. ROTACIÓN: Ángulo formado por el vector Muñeca -> Dedo corazón
            # Le sumamos 90 grados para que cuando la mano esté vertical, el ángulo sea 0.
            angulo_virtual = calcular_angulo(p_wrist, p_middle) + 90

            # 2. ESCALA (Z-Depth aproximado): Inversamente proporcional a la distancia en la imagen.
            # Cuanto más cerca la mano de la cámara, mayor es la distancia en píxeles entre los nudillos.
            distancia_palma_px = calcular_distancia(p_index, p_pinky)
            # Normalizamos un poco la escala para que el cubo mida entre 50 y 300 px
            escala_virtual = int(distancia_palma_px * 2.5) 
            escala_virtual = max(20, min(400, escala_virtual))

            # Feedback visual de los vectores
            cv.line(frame, p_wrist, p_middle, (255, 0, 0), 2)
            cv.line(frame, p_index, p_pinky, (0, 255, 0), 2)


        # --- RENDERIZAR OBJETO VIRTUAL CONTROLADO ---
        # Posicionarlo en el centro de la pantalla
        cx, cy = w // 2, h // 2
        
        if detectado:
            # Crear un cuadrado rotado
            rect = ((cx, cy), (escala_virtual, escala_virtual), angulo_virtual)
            box = cv.boxPoints(rect)
            box = np.int32(box)
            
            # Dibujar polígono rotado y rellenado
            cv.drawContours(frame, [box], 0, (0, 150, 255), 2) # Borde
            
            # Poner texto informativo
            texto_info = f"Rotacion: {int(angulo_virtual)} grados | Escala: {escala_virtual}"
            putText(frame, texto_info, (10, 30), color=(0, 255, 0))
        else:
            putText(frame, "Esperando detectar una mano...", (10, 30), color=(0, 0, 255))
            # Dibujar cuadrado por defecto aburrido
            cv.rectangle(frame, (cx - 50, cy - 50), (cx + 50, cy + 50), (128, 128, 128), 2)

        cv.imshow('Controlador Sin Contacto (Manos)', frame)

        if key == 27 or key == ord('q'):
            break

cv.destroyAllWindows()
