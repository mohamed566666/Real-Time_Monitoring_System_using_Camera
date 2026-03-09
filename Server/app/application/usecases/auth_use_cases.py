from typing import List, Optional, Tuple
import numpy as np
from app.application.services.user_service import UserService
from app.application.services.face_embedding_service import FaceEmbeddingService
from app.infrastructure.aiModels.face_engine import FaceEngine


class VerifyUserIdentityUseCase:
    def __init__(
        self,
        user_service: UserService,
        embedding_service: FaceEmbeddingService,
        face_engine: FaceEngine,
        similarity_threshold: float = 0.7,
    ):
        self.user_service = user_service
        self.embedding_service = embedding_service
        self.face_engine = face_engine
        self.similarity_threshold = similarity_threshold

    def calculate_similarity(self, emb1: List[float], emb2: List[float]) -> float:
        a = np.array(emb1)
        b = np.array(emb2)

        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        similarity = dot_product / (norm_a * norm_b)
        return float(similarity)

    def find_best_match(
        self, input_embedding: List[float], stored_embeddings: List[List[float]]
    ) -> Tuple[Optional[List[float]], float]:
        if not stored_embeddings:
            return None, 0.0

        best_similarity = 0.0
        best_match = None

        for stored_emb in stored_embeddings:
            similarity = self.calculate_similarity(input_embedding, stored_emb)
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = stored_emb

        return best_match, best_similarity

    def find_best_match_with_index(
        self, input_embedding: List[float], stored_embeddings: List[List[float]]
    ) -> Tuple[Optional[List[float]], float, Optional[int]]:
        if not stored_embeddings:
            return None, 0.0, None

        best_similarity = 0.0
        best_match = None
        best_index = None

        for i, stored_emb in enumerate(stored_embeddings):
            similarity = self.calculate_similarity(input_embedding, stored_emb)
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = stored_emb
                best_index = i

        return best_match, best_similarity, best_index

    async def execute(self, username: str, input_embedding: List[float]) -> dict:
        user = await self.user_service.get_user_by_username(username)
        if not user:
            raise ValueError(f"User with username '{username}' not found")

        user_embeddings = await self.embedding_service.get_embeddings_by_user(user.id)
        if not user_embeddings:
            raise ValueError(f"No face embeddings found for user '{username}'")

        stored_embeddings = [emb.embedding for emb in user_embeddings]

        best_match, similarity, best_index = self.find_best_match_with_index(
            input_embedding, stored_embeddings
        )

        if best_match is None or similarity < self.similarity_threshold:
            return {
                "verified": False,
                "message": "Face verification failed",
                "similarity": similarity,
                "threshold": self.similarity_threshold,
                "best_match_index": best_index,
            }

        return {
            "verified": True,
            "message": "Face verification successful",
            "user": {
                "id": user.id,
                "name": user.name,
                "username": user.username,
                "role": user.role,
                "department_id": user.department_id,
            },
            "similarity": similarity,
            "threshold": self.similarity_threshold,
            "best_match_index": best_index,
        }


class VerifyUserWithImageUseCase:

    def __init__(
        self, verify_usecase: VerifyUserIdentityUseCase, face_engine: FaceEngine
    ):
        self.verify_usecase = verify_usecase
        self.face_engine = face_engine

    async def execute(self, username: str, image_bytes: bytes) -> dict:

        try:
            import cv2
            import numpy as np

            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                raise ValueError("Invalid image file")

            face = self.face_engine.detect_face(img)
            if face is None:
                raise ValueError("No face detected in the image")

            embedding = self.face_engine.get_embedding(face)

            result = await self.verify_usecase.execute(username, embedding)
            return result

        except Exception as e:
            raise ValueError(f"Face verification failed: {str(e)}")
