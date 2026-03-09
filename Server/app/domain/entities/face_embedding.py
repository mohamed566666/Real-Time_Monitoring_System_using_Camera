from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
import numpy as np


@dataclass
class FaceEmbedding:
    id: Optional[int]
    user_id: int
    embedding: List[float]
    created_at: Optional[datetime] = None

    def to_numpy(self) -> np.ndarray:
        return np.array(self.embedding)

    def cosine_similarity(self, other: "FaceEmbedding") -> float:
        a = self.to_numpy()
        b = other.to_numpy()
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    def is_match(self, other: "FaceEmbedding", threshold: float = 0.5) -> bool:
        return self.cosine_similarity(other) > threshold
