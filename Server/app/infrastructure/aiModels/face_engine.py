import os
import cv2
import numpy as np
import onnxruntime as ort
from typing import List, Tuple, Optional




def _find_server_root() -> str:
    current = os.path.abspath(os.path.dirname(__file__))
    for _ in range(8):
        if os.path.isdir(os.path.join(current, "models")) and os.path.isdir(
            os.path.join(current, "MobileFaceNet")
        ):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))


BASE_DIR = _find_server_root()

_REFERENCE_LANDMARKS = np.array(
    [
        [38.2946, 51.6963],
        [73.5318, 51.5014],
        [56.0252, 71.7366],
        [41.5493, 92.3655],
        [70.7299, 92.2041],
    ],
    dtype=np.float32,
)


class FaceEngine:

    def __init__(self, recognition_threshold: float = 0.6):
        self.threshold = recognition_threshold

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


    def detect_face(self, image: np.ndarray) -> Optional[np.ndarray]:
        h, w = image.shape[:2]
        blob = cv2.dnn.blobFromImage(
            cv2.resize(image, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0)
        )
        self.detector.setInput(blob)
        detections = self.detector.forward()

        best_conf = 0.0
        best_face = None
        for i in range(detections.shape[2]):
            conf = float(detections[0, 0, i, 2])
            if conf > 0.7 and conf > best_conf:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                x1, y1, x2, y2 = box.astype("int")
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)
                crop = image[y1:y2, x1:x2]
                if crop.size > 0:
                    best_face = crop
                    best_conf = conf
        return best_face

    def detect_all_faces(self, image: np.ndarray) -> List[dict]:
        h, w = image.shape[:2]
        blob = cv2.dnn.blobFromImage(
            cv2.resize(image, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0)
        )
        self.detector.setInput(blob)
        detections = self.detector.forward()
        faces = []
        for i in range(detections.shape[2]):
            conf = float(detections[0, 0, i, 2])
            if conf > 0.5:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                x1, y1, x2, y2 = box.astype("int")
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)
                faces.append(
                    {
                        "face": image[y1:y2, x1:x2],
                        "confidence": conf,
                        "bbox": (x1, y1, x2, y2),
                    }
                )
        return faces


    def _align_face(self, face_img: np.ndarray) -> np.ndarray:
        lab = cv2.cvtColor(face_img, cv2.COLOR_BGR2LAB)
        l_ch, a_ch, b_ch = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
        l_ch = clahe.apply(l_ch)
        lab = cv2.merge([l_ch, a_ch, b_ch])
        return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    def preprocess(self, face_img: np.ndarray) -> np.ndarray:
        aligned = self._align_face(face_img)
        resized = cv2.resize(aligned, (112, 112))
        blob = cv2.dnn.blobFromImage(
            resized,
            scalefactor=1.0 / 127.5,
            size=(112, 112),
            mean=(127.5, 127.5, 127.5),
            swapRB=True,
            crop=False,
            ddepth=cv2.CV_32F,
        )
        return blob


    def get_embedding(self, face_img: np.ndarray) -> List[float]:
        input_data = self.preprocess(face_img)
        outputs = self.session.run([self.output_name], {self.input_name: input_data})
        embedding = outputs[0].flatten()

        norm = np.linalg.norm(embedding)
        if norm > 1e-10:
            embedding = embedding / norm

        return embedding.tolist()


    def calculate_similarity(self, emb1: List[float], emb2: List[float]) -> float:
        a = np.array(emb1, dtype=np.float32)
        b = np.array(emb2, dtype=np.float32)
        return float(np.dot(a, b))

    def verify_face(
        self,
        face_img,
        stored_embedding: List[float],
        threshold: Optional[float] = None,
        embedding_override: Optional[List[float]] = None,
    ) -> Tuple[bool, float]:
        t = threshold if threshold is not None else self.threshold
        embedding = (
            embedding_override
            if embedding_override is not None
            else self.get_embedding(face_img)
        )
        similarity = self.calculate_similarity(embedding, stored_embedding)
        return similarity >= t, similarity
