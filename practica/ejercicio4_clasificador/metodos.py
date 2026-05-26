import cv2 as cv
import numpy as np
import os
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from umucv.util import check_and_download

class MetodoClasificacion:
    def preprocesar_modelo(self, img):
        """Devuelve los descriptores o datos necesarios del modelo."""
        raise NotImplementedError
    
    def procesar_frame(self, frame):
        """Devuelve los datos del frame actual para comparar."""
        raise NotImplementedError

    def comparar(self, desc_frame, desc_modelo):
        """Devuelve una medida de similitud o distancia (menor = más parecido)."""
        raise NotImplementedError

class MetodoSIFT(MetodoClasificacion):
    def __init__(self):
        self.sift = cv.SIFT_create(nfeatures=500)
        self.matcher = cv.BFMatcher()

    def preprocesar_modelo(self, img):
        _, des = self.sift.detectAndCompute(img, None)
        return des

    def procesar_frame(self, frame):
        _, des = self.sift.detectAndCompute(frame, None)
        return des

    def comparar(self, des_frame, des_modelo):
        if des_frame is None or des_modelo is None:
            return float('inf')
        matches = self.matcher.knnMatch(des_frame, des_modelo, k=2)
        good = []
        for m in matches:
            if len(m) == 2:
                best, second = m
                if best.distance < 0.75 * second.distance:
                    good.append(best)
        # Devolvemos el negativo del número de coincidencias porque a más coincidencias, mejor (menor "distancia")
        return -len(good)

class MetodoEmbedder(MetodoClasificacion):
    def __init__(self):
        model_path = 'embedder.tflite'
        url = "https://storage.googleapis.com/mediapipe-models/image_embedder/mobilenet_v3_small/float32/1/mobilenet_v3_small.tflite"
        check_and_download(model_path, url)
        
        options = vision.ImageEmbedderOptions(
            base_options=python.BaseOptions(model_asset_path=model_path),
            l2_normalize=True, quantize=False)
        self.embedder = vision.ImageEmbedder.create_from_options(options)

    def _get_embedding(self, img):
        rgb = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = self.embedder.embed(mp_image)
        return result.embeddings[0]

    def preprocesar_modelo(self, img):
        return self._get_embedding(img)

    def procesar_frame(self, frame):
        return self._get_embedding(frame)

    def comparar(self, emb_frame, emb_modelo):
        # 1 - similitud coseno (distancia coseno)
        sim = vision.ImageEmbedder.cosine_similarity(emb_frame, emb_modelo)
        return 1.0 - sim

class MetodoManos(MetodoClasificacion):
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5)

    def _get_landmarks(self, img):
        rgb = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        results = self.hands.process(rgb)
        if results.multi_hand_landmarks:
            landmarks = results.multi_hand_landmarks[0].landmark
            return np.array([[lm.x, lm.y, lm.z] for lm in landmarks])
        return None

    def _normalize(self, points):
        points = points - np.mean(points, axis=0)
        norm = np.linalg.norm(points)
        if norm > 0:
            points /= norm
        return points

    def preprocesar_modelo(self, img):
        lm = self._get_landmarks(img)
        return self._normalize(lm) if lm is not None else None

    def procesar_frame(self, frame):
        lm = self._get_landmarks(frame)
        return self._normalize(lm) if lm is not None else None

    def comparar(self, lm_frame, lm_modelo):
        if lm_frame is None or lm_modelo is None:
            return float('inf')
            
        # Centrar las nubes de puntos en el origen para independizar de la traslación
        lm_frame_centrado = lm_frame - np.mean(lm_frame, axis=0)
        lm_modelo_centrado = lm_modelo - np.mean(lm_modelo, axis=0)

        # Calculamos la matriz de covarianza cruzada para encontrar la rotación óptima
        H = lm_frame_centrado.T @ lm_modelo_centrado
        
        # Descomposición en Valores Singulares (SVD)
        U, S, Vt = np.linalg.svd(H)
        
        # Obtenemos la matriz de rotación R
        R = U @ Vt
        
        # Evitamos reflexiones matemáticas (espejos)
        if np.linalg.det(R) < 0:
            Vt[-1, :] *= -1
            R = U @ Vt
            
        # Rotamos el esqueleto actual para que "encaje" en el ángulo del modelo original
        lm_frame_alineado = lm_frame @ R
        
        # Ahora comparamos la distancia pura, sin el sesgo del ángulo
        return np.linalg.norm(lm_frame_alineado - lm_modelo)
