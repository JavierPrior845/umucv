#!/usr/bin/env python

import numpy as np
import cv2 as cv
import os
import time
import datetime
import yaml
from collections import deque
from ultralytics import YOLO

from umucv.stream import autoStream
from umucv.util import ROI, putText, check_and_download, Video

# --- CONFIGURACIÓN ---
# Categorías de interés (COCO names)
INTEREST_CATEGORIES = ['person', 'dog', 'cat', 'bicycle', 'motorcycle']
# Umbral de confianza para YOLO
CONF_THRESHOLD = 0.5
# Umbral de movimiento (píxeles blancos en ROI)
MOTION_THRESHOLD = 1000 
# Duración típica del clip (segundos)
RECORD_SECONDS = 3
# Buffer de frames anteriores al movimiento (para no perder el inicio)
PRE_ROLL_SECONDS = 1

# --- INICIALIZACIÓN YOLO ---
print("Cargando modelo YOLO...")
model = YOLO("yolo11n.pt")
url_coco = "https://raw.githubusercontent.com/ultralytics/ultralytics/refs/heads/main/ultralytics/cfg/datasets/coco.yaml"
check_and_download("coco.yaml", url_coco)
labels = yaml.safe_load(open("coco.yaml"))['names']

# --- TELEGRAM (Configura esto para que funcione) ---
# Puedes usar un archivo .env o hardcodearlo para pruebas
TELEGRAM_TOKEN = "8530334918:AAGM9pG7Ah2dhrwjrJDhS6UgIK7iXqDAx1Y"
CHAT_ID = "5551685530"

def send_telegram_notification(message, photo_path=None):
    """
    Función placeholder para enviar notificaciones.
    Requiere requests instalado.
    """
    import requests
    print(f"NOTIFICACIÓN TELEGRAM: {message}")
    if TELEGRAM_TOKEN == "TU_TOKEN_AQUI":
        print("Aviso: Configura el Token de Telegram para recibir alertas reales.")
        return
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={'chat_id': CHAT_ID, 'text': message})
        if photo_path:
            url_photo = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
            with open(photo_path, 'rb') as photo:
                requests.post(url_photo, data={'chat_id': CHAT_ID}, files={'photo': photo})
    except Exception as e:
        print(f"Error enviando Telegram: {e}")

# --- UTILIDADES ---
def anonymize(frame, boxes):
    """Aplica un blur fuerte a las zonas de personas detectadas."""
    for (x1, y1, x2, y2) in boxes:
        # Asegurar límites dentro del frame
        h, w = frame.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        
        roi = frame[y1:y2, x1:x2]
        if roi.size > 0:
            # Pixelado rápido: reducir y ampliar o Blur
            blur = cv.GaussianBlur(roi, (51, 51), 30)
            frame[y1:y2, x1:x2] = blur

# --- BUCLE PRINCIPAL ---
region = ROI("Vigilancia")
bgsub = cv.createBackgroundSubtractorMOG2(500, 16, False)

# Buffer para el pre-roll
frame_buffer = deque()
recording = False
record_start_time = 0
video_writer = None
interesting_event = False
event_label = ""

print("\nSISTEMA DE VIGILANCIA ACTIVO")
print("1. Dibuja un rectángulo en la ventana 'Vigilancia' para definir el ROI.")
print("2. El sistema detectará movimiento y grabará clips cuando vea algo interesante.")
print("3. Pulsa 'ESC' para salir.\n")

for key, frame in autoStream():
    display_frame = frame.copy()
    h, w = frame.shape[:2]
    
    # Estimación de FPS para el pre-roll buffer (asumimos ~20 si no detectamos)
    fps_approx = 20
    if len(frame_buffer) > (PRE_ROLL_SECONDS * fps_approx):
        frame_buffer.popleft()
    frame_buffer.append(frame.copy())

    if region.roi:
        [x1, y1, x2, y2] = region.roi
        cv.rectangle(display_frame, (x1, y1), (x2, y2), (255, 255, 0), 2)
        
        # Recortar ROI para detección de movimiento
        roi_motion = frame[y1:y2+1, x1:x2+1]
        if roi_motion.size > 0:
            fgmask = bgsub.apply(roi_motion)
            # Limpiar máscara
            _, fgmask = cv.threshold(fgmask, 200, 255, cv.THRESH_BINARY)
            fgmask = cv.erode(fgmask, None, iterations=1)
            fgmask = cv.dilate(fgmask, None, iterations=2)
            
            motion_score = np.sum(fgmask == 255)
            
            # Mostrar máscara para debug
            cv.imshow("Mascara ROI", fgmask)

            # Lógica de disparo de evento
            if not recording and motion_score > MOTION_THRESHOLD:
                print("¡Movimiento detectado! Analizando...")
                recording = True
                record_start_time = time.time()
                interesting_event = False
                
                # Crear VideoWriter
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                video_filename = f"captura_{timestamp}.avi"
                fourcc = cv.VideoWriter_fourcc(*'XVID')
                video_writer = cv.VideoWriter(video_filename, fourcc, 20.0, (w, h))
                
                # Volcar el pre-roll buffer al video
                for f in frame_buffer:
                    video_writer.write(f)

    if recording:
        results = model(frame, verbose=False)
        people_boxes = []
        found_now = False
        
        for r in results:
            for b in r.boxes:
                conf = b.conf.item()
                if conf > CONF_THRESHOLD:
                    cls_id = int(b.cls.item())
                    label = labels[cls_id]
                    coords = b.xyxy[0].cpu().numpy().astype(int)
                    
                    if label in INTEREST_CATEGORIES:
                        interesting_event = True
                        event_label = label
                        found_now = True
                        if label == 'person':
                            people_boxes.append(coords)
                        
                        cv.rectangle(display_frame, (coords[0], coords[1]), (coords[2], coords[3]), (0, 255, 0), 2)
                        putText(display_frame, f"{label} {conf:.2f}", (coords[0], coords[1]-10))

        # Anonimizar personas en el frame que se guarda
        save_frame = frame.copy()
        if people_boxes:
            anonymize(save_frame, people_boxes)
            anonymize(display_frame, people_boxes) # También en pantalla para ver que funciona

        video_writer.write(save_frame)
        
        # Comprobar si termina el tiempo de grabación
        if time.time() - record_start_time > RECORD_SECONDS:
            recording = False
            video_writer.release()
            print(f"Vídeo guardado: {video_filename}")
            
            if interesting_event:
                msg = f"Evento detectado: {event_label} en zona de vigilancia."
                # Guardar el frame actual como captura para telegram
                snap_path = f"snap_{timestamp}.jpg"
                cv.imwrite(snap_path, display_frame)
                send_telegram_notification(msg, snap_path)
            else:
                print("Movimiento detectado pero no era ningún objeto de interés.")
                # os.remove(video_filename)

    cv.imshow("Vigilancia", display_frame)
    if key == 27: break

if video_writer:
    video_writer.release()
cv.destroyAllWindows()
