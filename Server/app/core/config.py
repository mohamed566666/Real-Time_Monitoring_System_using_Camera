from pydantic_settings import BaseSettings
from typing import Optional, List
import os

class Settings(BaseSettings):
    DATABASE_URL: str
    
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    DATABASE_POOL_SIZE: Optional[int] = 10
    DATABASE_MAX_OVERFLOW: Optional[int] = 20
    DATABASE_ECHO: Optional[bool] = False
    
    APP_NAME: Optional[str] = "Real-Time Employees Monitoring System"
    DEBUG: Optional[bool] = True
    HOST: Optional[str] = "0.0.0.0"
    PORT: Optional[int] = 8000
    ENVIRONMENT: Optional[str] = "development"
    
    CORS_ORIGINS: List[str] = ["*"]
    
    MODELS_PATH: Optional[str] = "./models"
    FACE_DETECTION_PROTOTXT: Optional[str] = "../models/deploy.prototxt"
    FACE_DETECTION_MODEL: Optional[str] = "../models/res10_300x300_ssd_iter_140000.caffemodel"
    FACE_RECOGNITION_MODEL: Optional[str] = "../models/MobileFaceNet/weights/mobilefacenet.onnx"
    FACE_DETECTION_CONFIDENCE: Optional[float] = 0.6
    FACE_RECOGNITION_THRESHOLD: Optional[float] = 0.6
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore" 

settings = Settings()