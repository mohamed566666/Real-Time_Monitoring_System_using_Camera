# app/infrastructure/aiModels/face_engine.py
import os
import cv2
import numpy as np
import onnxruntime as ort
from typing import List, Optional, Tuple


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))


class FaceEngine:

    def __init__(self):

        detector_proto = os.path.join(BASE_DIR, "models/deploy.prototxt")
        detector_model = os.path.join(
            BASE_DIR, "models/res10_300x300_ssd_iter_140000.caffemodel"
        )

        self.detector = cv2.dnn.readNetFromCaffe(detector_proto, detector_model)

        recognition_model = os.path.join(
            BASE_DIR, "MobileFaceNet/weights/mobilefacenet.onnx"
        )

        self.session = ort.InferenceSession(recognition_model)

        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name

    def detect_face(self, image: np.ndarray):
        """Detect face in image - returns first face found"""
        h, w = image.shape[:2]

        blob = cv2.dnn.blobFromImage(
            cv2.resize(image, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0)
        )

        self.detector.setInput(blob)
        detections = self.detector.forward()

        best_conf = 0
        best_face = None

        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.7 and confidence > best_conf:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (x1, y1, x2, y2) = box.astype("int")

                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)

                best_face = image[y1:y2, x1:x2]
                best_conf = confidence

        return best_face

    def detect_all_faces(self, image: np.ndarray):
        """Detect all faces in image - returns list of faces"""
        h, w = image.shape[:2]
        faces = []

        blob = cv2.dnn.blobFromImage(
            cv2.resize(image, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0)
        )

        self.detector.setInput(blob)
        detections = self.detector.forward()

        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.5:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (x1, y1, x2, y2) = box.astype("int")

                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)

                face = image[y1:y2, x1:x2]
                faces.append(
                    {
                        "face": face,
                        "confidence": float(confidence),
                        "bbox": (x1, y1, x2, y2),
                    }
                )

        return faces

    def preprocess(self, face_img):
        """Preprocess face for embedding extraction"""
        face_resized = cv2.resize(face_img, (112, 112))
        blob = cv2.dnn.blobFromImage(
            face_resized,
            1.0 / 127.5,
            (112, 112),
            127.5,
            True,
            False,
            cv2.CV_32F,
        )
        return blob

    def get_embedding(self, face_img):
        """Extract embedding from face image"""
        input_data = self.preprocess(face_img)
        outputs = self.session.run([self.output_name], {self.input_name: input_data})
        embedding = outputs[0].flatten()

        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 1e-10:
            embedding = embedding / norm

        return embedding.tolist()

    def calculate_similarity(self, emb1: List[float], emb2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        a = np.array(emb1)
        b = np.array(emb2)

        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        similarity = dot_product / (norm_a * norm_b)
        return float(similarity)

    def verify_face(
        self, face_img, stored_embedding: List[float], threshold: float = 0.7
    ) -> Tuple[bool, float]:
        """Verify if face matches stored embedding"""
        # Extract embedding from face
        input_embedding = self.get_embedding(face_img)

        # Calculate similarity
        similarity = self.calculate_similarity(input_embedding, stored_embedding)

        # Check if above threshold
        return similarity >= threshold, similarity
