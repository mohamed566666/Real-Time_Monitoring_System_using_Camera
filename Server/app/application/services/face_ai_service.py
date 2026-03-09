import numpy as np
import cv2
from app.infrastructure.aiModels.face_engine import FaceEngine


class FaceAIService:

    def __init__(self):
        self.engine = FaceEngine()

    async def extract_embedding_from_bytes(self, image_bytes: bytes):

        np_array = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError("Invalid image")

        face = self.engine.detect_face(image)

        if face is None:
            raise ValueError("No face detected")

        embedding = self.engine.get_embedding(face)

        return embedding
