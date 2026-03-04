# Real-Time Monitoring System

A powerful real-time face recognition monitoring system built with FastAPI and modern deep learning techniques. This system provides comprehensive APIs for user management, department organization, device monitoring, and face recognition capabilities.

## 📋 Prerequisites

- **Python**: Version 3.8 or higher
- **PostgreSQL**: Version 12 or higher

## 🚀 Technology Stack

- **Framework**: FastAPI (Python 3.8+)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **AI/ML**: OpenCV, Face Recognition models (MobileFaceNet)

## 📁 Project Structure

## 📁 Project Structure

```
face-recognition-api/
├── server/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── application/
│   │   │   ├── __init__.py
│   │   │   ├── services/
│   │   │   └── usecases/
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   └── dependencies.py
│   │   ├── domain/
│   │   │   ├── __init__.py
│   │   │   └── entities/
│   │   ├── infrastructure/
│   │   │   ├── __init__.py
│   │   │   ├── aiModels/
│   │   │   │   ├── __init__.py
│   │   │   │   └── face_engine.py
│   │   │   ├── db/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py
│   │   │   │   ├── database.py
│   │   │   │   └── models.py
│   │   │   └── repositories/
│   │   │       ├── __init__.py
│   │   │       ├── base_repository.py
│   │   │       └── implementations/
│   │   └── presentation/
│   │       ├── __init__.py
│   │       └── controllers/
│   │           ├── __init__.py
│   │           ├── auth_controller.py
│   │           ├── user_controller.py
│   │           ├── department_controller.py
│   │           ├── device_controller.py
│   │           └── face_embedding_controller.py
│   ├── models/
│   │   ├── .gitkeep
│   │   ├── deploy.prototxt
│   │   ├── res10_300x300_ssd_iter_140000.caffemodel
│   │   └── MobileFaceNet/
│   │       └── weights/
│   │           └── mobilefacenet.onnx
│   └── requirements.txt
└── README.md
```

## 🔧 Installation

### 1. Clone the Repository

### 2. Create Virtual Environment

# Windows

python -m venv venv
venv\Scripts\activate

# Linux/Mac

python3 -m venv venv
source venv/bin/activate

### 3. Install Dependencies

cd server
pip install -r requirements.txt

### 4. Download Model Files

Place the following model files in the server/models/ directory:

Face Detection Model:

deploy.prototxt

res10_300x300_ssd_iter_140000.caffemodel

Face Recognition Model:

MobileFaceNet/weights/mobilefacenet.onnx

### 5- Initialize Database

### 🏃‍♂️ Running the Application

uvicorn app.main:app --reload
